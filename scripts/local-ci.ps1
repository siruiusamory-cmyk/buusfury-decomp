# local-ci.ps1 - a local full-CI record for one SHA.
#
# GitLab cannot create a pipeline while the namespace is over its CI-minutes
# quota, so a record produced here on an exact SHA is the temporary gate. The
# script checks the SHA out as a LINKED WORKTREE (a plain clone makes
# test_pre_merge_check refuse wrongly: a clone is not a linked worktree), builds
# a fresh venv, runs the four tree-wide quality gates, the portable suite at
# --dist loadfile, the adjacency orders and the ROM-free integration member, and
# writes build/local-ci/<sha>/record.txt with its own sha256.
#
# PowerShell 5.1 traps this file is written around, each measured:
#  - 'Stop' turns a native command's stderr into a terminating error, so the
#    preference stays 'Continue' and every call is checked by $LASTEXITCODE.
#  - An array argument needs param([string[]]) to splat; without it git gets one
#    malformed argument and answers with its usage text.
#  - THE CARET IS CONSUMED IN A NATIVE ARGUMENT EVEN WHEN QUOTED: `<sha>^{tree}`
#    reaches git as `<sha>^tree`. The brace-free `show -s --format=%T` is used.
#  - StandardOutputEncoding requires RedirectStandardOutput to be set first.
#
# USE:
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\local-ci.ps1 -Sha <40-hex> [-Workers N]

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Sha,
    [int]$Workers = 4,
    [string]$RepoPath,

    # Pinned per-file skip counts, keyed by repository-relative path. A pinned
    # file that IS present is an equality gate; a pinned file ABSENT from the SHA
    # is recorded as not applicable, never a failure, because an absent file
    # cannot legitimately skip anything. Default: the 13 PowerShell nodes of the
    # CI trace job 17121704860 at 9c34f1ae, for trees that carry them.
    [hashtable]$PinnedSkips = @{
        'tests/unit/test_dev_tools.py'       = 6
        'tests/unit/test_worktree_owners.py' = 7
    },

    [string]$PinnedTraceJob = '17121704860',
    [string]$PinnedTraceSha = '9c34f1aebba6f9a4b158d91726f0f816840a8f4',
    [int]$PinnedSuiteSkips = 320,

    # Drive the fail-closed paths. -ForceTimeoutSeconds N makes the FIRST step
    # behave as though the budget had expired, so the kill path can be shown.
    [int]$ForceTimeoutSeconds = 0,

    # Drive the skip-count failure: pin one path to a deliberately wrong count.
    # `powershell -File` cannot pass a hashtable, so the drive needs its own
    # switch rather than -PinnedSkips.
    [string]$PinOnePath = '',
    [int]$PinOneCount = -1
)

$ErrorActionPreference = 'Continue'
if ($PinOnePath) {
    $PinnedSkips = @{ $PinOnePath = $PinOneCount }
    $script:DroveSkipPath = $true
} else {
    $script:DroveSkipPath = $false
}
$script:BudgetSeconds = 45 * 60
$script:Stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
$script:Steps = New-Object System.Collections.Generic.List[object]
$script:Failures = New-Object System.Collections.Generic.List[string]
$script:Notes = New-Object System.Collections.Generic.List[string]
$script:Timeouts = 0
$script:DroveSkipPath = $false
$script:Cleaned = $false

if (-not $RepoPath) { $RepoPath = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path }

# --- where this RUN keeps its evidence ----------------------------------------
# The canonical record path stays where callers look for it, and every run also gets
# its own directory named from the clock plus a guid, so a later run on the same SHA
# cannot overwrite an earlier run's preserved captures or its copy of the record.
#: $recordDir is under ignored build/; nothing here is ever committed or printed.
$recordDir = Join-Path (Join-Path $RepoPath 'build') (Join-Path 'local-ci' $Sha)
$runId = (Get-Date -Format 'yyyyMMdd-HHmmss') + '-' + [Guid]::NewGuid().ToString('N').Substring(0, 6)
$runDir = Join-Path (Join-Path $recordDir 'runs') $runId
$script:StepsDir = Join-Path $runDir 'steps'

function Write-Log { param([string]$Text) Write-Host ("[{0,7:N1}s] {1}" -f $script:Stopwatch.Elapsed.TotalSeconds, $Text) }
function Add-Failure { param([string]$Text) $script:Failures.Add($Text); Write-Log ("FAIL: $Text") }

#: Remove the throwaway linked worktree and the neutral clone. Every exit path
#: reaches it: the explicit call before the record is written, and the finally
#: that covers an early exit or an abrupt stop. Idempotent, so those two calls
#: cannot double-report. The worktree is removed from the NEUTRAL clone, which is
#: the repository that owns it; the earlier code removed it from $RepoPath, a
#: different repository, which left the clone and sometimes the worktree behind.
function Invoke-CiTidy {
    if ($script:Cleaned) { return }
    $script:Cleaned = $true
    $worktreeRemoved = (-not $worktree) -or (-not (Test-Path -LiteralPath $worktree))
    if (-not $worktreeRemoved) {
        & git -C $neutral worktree remove --force $worktree 2>&1 | ForEach-Object { Write-Host $_ }
        $worktreeRemoved = -not (Test-Path -LiteralPath $worktree)
        if (-not $worktreeRemoved) { Remove-Item -LiteralPath $worktree -Recurse -Force -ErrorAction SilentlyContinue }
        $worktreeRemoved = -not (Test-Path -LiteralPath $worktree)
    }
    $neutralRemoved = (-not $neutral) -or (-not (Test-Path -LiteralPath $neutral))
    if (-not $neutralRemoved) {
        Remove-Item -LiteralPath $neutral -Recurse -Force -ErrorAction SilentlyContinue
        $neutralRemoved = -not (Test-Path -LiteralPath $neutral)
    }
    if (-not $worktreeRemoved) { Add-Failure 'the throwaway worktree could not be removed' }
    if (-not $neutralRemoved) { Add-Failure 'the neutral clone could not be removed' }
    Write-Log ("worktree removed: {0}; neutral clone removed: {1}" -f $worktreeRemoved, $neutralRemoved)
}

function Get-TreeBytes {
    param([int]$RootPid)
    try {
        $all = Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" -ErrorAction SilentlyContinue |
            Select-Object ProcessId, ParentProcessId
        $ids = New-Object System.Collections.Generic.HashSet[int]
        $null = $ids.Add($RootPid)
        $changed = $true
        while ($changed) {
            $changed = $false
            foreach ($p in $all) {
                if ($ids.Contains([int]$p.ParentProcessId) -and -not $ids.Contains([int]$p.ProcessId)) {
                    $null = $ids.Add([int]$p.ProcessId); $changed = $true
                }
            }
        }
        $now = 0
        foreach ($id in $ids) {
            $ws = (Get-Process -Id $id -ErrorAction SilentlyContinue).WorkingSet64
            if ($ws) { $now += $ws }
        }
        return $now
    } catch { return 0 }
}

# Run one step in a CHILD powershell so the 45-minute budget can kill its whole
# process tree. A step that overruns is killed with taskkill /T /F and is a FAIL.
function Invoke-Step {
    param(
        [Parameter(Mandatory)][string]$Name,
        [Parameter(Mandatory)][string]$FilePath,
        [Parameter(Mandatory)][string[]]$Arguments,
        [string]$WorkDir
    )
    $remaining = [math]::Max(1, $script:BudgetSeconds - [math]::Floor($script:Stopwatch.Elapsed.TotalSeconds))
    if ($ForceTimeoutSeconds -gt 0 -and $script:Steps.Count -eq 0) {
        $remaining = $ForceTimeoutSeconds
        $script:Notes.Add("timeout path driven with -ForceTimeoutSeconds $ForceTimeoutSeconds on the first step")
    }
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $quoted = ($Arguments | ForEach-Object { '"' + $_ + '"' }) -join ' '
    #: Each step's streams are captured into THIS RUN's own directory and KEPT. They used
    #: to go to two fixed files in the temporary directory, which were read into memory
    #: and deleted, so a failed step left no output anywhere and the 05b759ad pip failure
    #: could not be established from the artifacts. The paths are private, under ignored
    #: build/, and are reported in the record by path and digest rather than by content.
    $index = $script:Steps.Count + 1
    $slug = ($Name -replace '[^A-Za-z0-9]+', '-').Trim('-')
    if (-not (Test-Path -LiteralPath $script:StepsDir)) { New-Item -ItemType Directory -Force -Path $script:StepsDir | Out-Null }
    $outFile = Join-Path $script:StepsDir ('{0:D2}-{1}.out' -f $index, $slug)
    $errFile = Join-Path $script:StepsDir ('{0:D2}-{1}.err' -f $index, $slug)
    $proc = Start-Process -FilePath $FilePath -ArgumentList $quoted -WorkingDirectory $WorkDir -NoNewWindow -PassThru `
        -RedirectStandardOutput $outFile `
        -RedirectStandardError $errFile
    #: Open the process handle NOW, while the step is still alive. Under Windows
    #: PowerShell 5.1 a redirected Start-Process polled on HasExited reports a
    #: NULL ExitCode once the process is gone, and the old null-to-zero mapping
    #: turned every step into exit 0, so a red quality gate or a red integration
    #: selection could not fail the record. Measured on 5.1.26100.9444 against a
    #: step exiting 5: reading .Handle here gives 5; reading nothing gives null;
    #: WaitForExit() or Refresh() alone still gives null.
    $null = $proc.Handle
    $peak = 0L
    $killed = $false
    while (-not $proc.HasExited) {
        $now = Get-TreeBytes -RootPid $proc.Id
        if ($now -gt $peak) { $peak = $now }
        if ($sw.Elapsed.TotalSeconds -ge $remaining) {
            Write-Log ("step '{0}' over its {1}s allowance: killing the process tree of pid {2}" -f $Name, $remaining, $proc.Id)
            & taskkill.exe /PID $proc.Id /T /F 2>&1 | Out-Null
            $killed = $true
            $script:Timeouts++
            Start-Sleep -Milliseconds 400
            break
        }
        Start-Sleep -Milliseconds 400
    }
    $sw.Stop()
    $out = ''
    $captures = @()
    foreach ($f in @($outFile, $errFile)) {
        if (Test-Path -LiteralPath $f) {
            $out += (Get-Content -LiteralPath $f -Raw)
            $captures += [pscustomobject]@{
                Path   = $f.Substring($RepoPath.Length + 1)
                Sha256 = (Get-FileHash -LiteralPath $f -Algorithm SHA256).Hash
                Bytes  = (Get-Item -LiteralPath $f).Length
            }
        }
    }
    if ($peak -gt $script:PeakBytes) { $script:PeakBytes = $peak }
    $code = if ($killed) { 124 } elseif ($null -ne $proc.ExitCode) { $proc.ExitCode } else { -1 }
    $entry = [pscustomobject]@{ Name = $Name; Exit = $code; Seconds = [math]::Round($sw.Elapsed.TotalSeconds, 1); Output = $out; Killed = $killed; Captures = $captures }
    $script:Steps.Add($entry)
    if ($killed) { Add-Failure ("step '{0}' exceeded its budget and was killed" -f $Name) }
    elseif ($code -eq -1) { Add-Failure ("step '{0}' finished with no readable exit code" -f $Name) }
    elseif ($code -ne 0) { Add-Failure ("step '{0}' exited {1}" -f $Name, $code) }
    return $entry
}

function Invoke-Git {
    param([Parameter(Mandatory)][string[]]$Arguments)
    $output = @(& git -C $RepoPath @Arguments 2>&1 | ForEach-Object { $_.ToString() })
    return [pscustomobject]@{ Exit = $LASTEXITCODE; Lines = $output; Text = (($output -join [Environment]::NewLine).Trim()) }
}

# --- the SHA ------------------------------------------------------------------
if ($Sha -notmatch '^[0-9a-f]{40}$') { Write-Host "local-ci: FAIL - -Sha must be a full 40-character lowercase hex SHA, got '$Sha'"; exit 1 }
$resolved = Invoke-Git -Arguments @('rev-parse', '--verify', $Sha)
if ($resolved.Exit -ne 0 -or $resolved.Text -ne $Sha) {
    Write-Host "local-ci: FAIL - $Sha does not resolve to itself in $RepoPath ($($resolved.Text))"
    exit 1
}

# --- host, memory, budget ----------------------------------------------------
$cores = [Environment]::ProcessorCount
$maxWorkers = [math]::Max(1, [math]::Floor($cores / 2))
if ($Workers -gt $maxWorkers) {
    Write-Log ("workers {0} clamped to {1} (half of {2} logical cores)" -f $Workers, $maxWorkers, $cores)
    $script:Notes.Add(("workers clamped from {0} to {1}" -f $Workers, $maxWorkers))
    $Workers = $maxWorkers
}
if ($Workers -lt 1) { $Workers = 1 }
$os = Get-CimInstance Win32_OperatingSystem
$hostName = $env:COMPUTERNAME
$totalGb = [math]::Round($os.TotalVisibleMemorySize / 1MB, 1)
$freeGb = [math]::Round($os.FreePhysicalMemory / 1MB, 1)
$script:PeakBytes = 0L
Write-Log ("host {0}: {1} cores, {2} GB RAM, {3} GB free; workers {4}" -f $hostName, $cores, $totalGb, $freeGb, $Workers)

# --- the linked worktree -----------------------------------------------------
# --- a NEUTRAL clone, then the linked worktree -------------------------------
# The worktree must NOT come from a ticket worktree: a checkout under a worktree
# is itself refused by scripts/pre-merge-check.ps1, and
# tests/unit/test_pre_merge_check.py fails on that for a reason unrelated to the
# SHA under test. A local clone is a primary checkout in its own right, so the
# worktree cut from it is an ordinary linked worktree and the suite sees the same
# shape CI gives it. Measured: in the clone, --git-dir is `.git`; in the worktree
# cut from it, an absolute path under the clone's .git/worktrees.
$sha8 = $Sha.Substring(0, 8)
$ciHome = Join-Path $env:LOCALAPPDATA 'log1-ci'
New-Item -ItemType Directory -Force -Path $ciHome | Out-Null
$neutral = Join-Path $ciHome ("neutral-" + $sha8)
$worktree = Join-Path $ciHome ("wt-" + $sha8)
foreach ($path in @($worktree, $neutral)) {
    if (Test-Path -LiteralPath $path) {
        & git -C $neutral worktree remove --force $path 2>&1 | Out-Null
        if (Test-Path -LiteralPath $path) { Remove-Item -LiteralPath $path -Recurse -Force -ErrorAction SilentlyContinue }
    }
}
#: Everything from here on runs under a finally that removes the throwaway
#: worktree and the neutral clone, so an early exit or an abrupt stop cannot leave
#: them behind. The block is not re-indented: the whitespace change would bury
#: this fix in the delta.
try {
$clone = Invoke-Git -Arguments @('clone', '--quiet', '--local', '--no-checkout', $RepoPath, $neutral)
if ($clone.Exit -ne 0) {
    Write-Host "local-ci: FAIL - could not clone $RepoPath to $neutral"
    exit 1
}
$add = Invoke-Git -Arguments @('-C', $neutral, 'worktree', 'add', '--detach', $worktree, $Sha)
if ($add.Exit -ne 0 -or -not (Test-Path -LiteralPath $worktree)) {
    Write-Host "local-ci: FAIL - could not add a worktree at $worktree for $Sha"
    exit 1
}
$treeShow = Invoke-Git -Arguments @('show', '-s', '--format=%T', $Sha)
$tree = $treeShow.Text
$subject = (Invoke-Git -Arguments @('log', '-n', '1', '--format=%s', $Sha)).Text
$dirty = (Invoke-Git -Arguments @('status', '--porcelain')).Text
if ($dirty) {
    Write-Host 'local-ci: FAIL - the source repository has uncommitted changes; the record would not describe the SHA alone'
    exit 1
}
Write-Log "worktree $worktree at $Sha (tree $tree)"

# --- the fresh venv ----------------------------------------------------------
$venv = Join-Path $env:LOCALAPPDATA ("log1-ci\local-ci-" + $sha8)
$venvPython = Join-Path $venv 'Scripts\python.exe'
if (Test-Path -LiteralPath $venv) { Remove-Item -LiteralPath $venv -Recurse -Force }
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $venv) | Out-Null
$pythonBase = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $pythonBase) { Write-Host 'local-ci: FAIL - no python on PATH'; exit 1 }
$null = Invoke-Step -Name 'venv create' -FilePath $pythonBase -Arguments @('-m', 'venv', $venv) -WorkDir $worktree
if (Test-Path -LiteralPath $venvPython) {
    $null = Invoke-Step -Name 'pip install -e .[dev,workbench,research]' -FilePath $venvPython -Arguments @('-m', 'pip', 'install', '--quiet', '--disable-pip-version-check', '-e', '.[dev,workbench,research]') -WorkDir $worktree
}
if (-not (Test-Path -LiteralPath $venvPython)) {
    Write-Host "local-ci: FAIL - no interpreter at $venvPython after the install step"
    exit 1
}
$env:QT_QPA_PLATFORM = 'offscreen'
$env:CLOUDFLARE_API_TOKEN = ''
$env:PYTEST_DEBUG_TEMPROOT = Join-Path ([System.IO.Path]::GetTempPath()) 'pytest-root'
$report = Join-Path $worktree 'report.xml'

# --- steps -------------------------------------------------------------------
foreach ($quality in @('public_surface', 'architecture', 'public_release', 'readability')) {
    $passed = @('-m', ('tools.quality.' + $quality))
    if ($quality -eq 'public_surface' -or $quality -eq 'readability') { $passed += '--all' }
    $null = Invoke-Step -Name ('tools.quality.' + $quality) -FilePath $venvPython -Arguments $passed -WorkDir $worktree
}

$pytestStep = Invoke-Step -Name ("pytest -n " + $Workers) -FilePath $venvPython -Arguments @('-m', 'pytest', 'tests/unit', '-q', '--dist', 'loadfile', '-n', "$Workers", '--junitxml=report.xml') -WorkDir $worktree

foreach ($order in @('forward', 'reverse')) {
    $null = Invoke-Step -Name ("adjacency " + $order) -FilePath $venvPython -Arguments @('-m', 'scripts.adjacency_run', '-Order', $order) -WorkDir $worktree
}

$null = Invoke-Step -Name 'test-integration selection' -FilePath $venvPython -Arguments @('-m', 'pytest', 'tests/integration/test_container_decode_synthetic.py', '-q') -WorkDir $worktree

# --- adjacency completeness --------------------------------------------------
foreach ($order in @('forward', 'reverse')) {
    $name = "adjacency " + $order
    $step = $script:Steps | Where-Object { $_.Name -eq $name } | Select-Object -First 1
    if (-not $step) { Add-Failure "no record for $name"; continue }
    if ($step.Exit -ne 0) { continue }
    if ($step.Output -match 'ran\s+\d+\s+modules\s+clean') { continue }
    Add-Failure "$name did not report a clean module run"
}

# --- skip counts -------------------------------------------------------------
$skipByFile = @{}
$failedCases = New-Object System.Collections.Generic.List[string]
$junitCounts = $null
if (Test-Path -LiteralPath $report) {
    $xml = [xml](Get-Content -LiteralPath $report -Raw)
    $suites = @($xml.testsuites.testsuite)
    $junitCounts = [pscustomobject]@{
        Tests    = ($suites | Measure-Object -Property tests -Sum).Sum
        Failures = ($suites | Measure-Object -Property failures -Sum).Sum
        Errors   = ($suites | Measure-Object -Property errors -Sum).Sum
        Skipped  = ($suites | Measure-Object -Property skipped -Sum).Sum
    }
    foreach ($case in $suites.testcase) {
        if ($case.failure -or $case.error) {
            $file = $case.file
            if (-not $file -and $case.classname) { $file = ($case.classname -replace '\.', '/') }
            $failedCases.Add(("$file::$($case.name)"))
        }
        if ($case.skipped) {
            $file = $case.file
            if (-not $file -and $case.classname) { $file = ($case.classname -replace '\.', '/') }
            if ($file) {
                if ($skipByFile.ContainsKey($file)) { $skipByFile[$file]++ } else { $skipByFile[$file] = 1 }
            }
        }
    }
} else {
    Add-Failure 'report.xml is missing, so the suite produced no machine-checkable result'
}
if ($junitCounts) {
    if ($junitCounts.Failures -gt 0 -or $junitCounts.Errors -gt 0) {
        Add-Failure ("junit reports {0} failures and {1} errors" -f $junitCounts.Failures, $junitCounts.Errors)
    }
    if ($pytestStep -and $pytestStep.Output -match '(\d+) skipped') {
        $summarySkips = [int]$Matches[1]
        if ($summarySkips -ne $junitCounts.Skipped) { Add-Failure ("summary says $summarySkips skipped, junit says $($junitCounts.Skipped)") }
    }
}
#: The pinned figures came from a Linux runner, where a `.ps1` cannot run and those
#: nodes SKIP. The condition the tests themselves skip on is `shutil.which("pwsh")
#: or shutil.which("powershell")`, so it is the condition here: a host WITH a
#: PowerShell runs those nodes, its per-file count is legitimately not the trace's,
#: and the equality does not apply. The record then says so with the count, never a
#: silent pass. A host with no PowerShell keeps the equality exactly as before.
$hasPowerShellHost = [bool]((Get-Command pwsh -ErrorAction SilentlyContinue) -or (Get-Command powershell -ErrorAction SilentlyContinue))
$pinnedApplicable = New-Object System.Collections.Generic.List[string]
$pinnedAbsent = New-Object System.Collections.Generic.List[string]
foreach ($file in $PinnedSkips.Keys) {
    if (-not (Test-Path -LiteralPath (Join-Path $worktree $file))) { $pinnedAbsent.Add($file); continue }
    $pinnedApplicable.Add($file)
    $actual = 0
    if ($skipByFile.ContainsKey($file)) { $actual = $skipByFile[$file] }
    if (-not $hasPowerShellHost -and $actual -ne $PinnedSkips[$file]) {
        Add-Failure ("$file skipped $actual, pinned $($PinnedSkips[$file]) from trace job $PinnedTraceJob at $($PinnedTraceSha.Substring(0,8))")
    }
}

#: The cleanup runs BEFORE the verdict is computed and before the record is
#: written, so a cleanup failure is part of the verdict instead of appearing only
#: in the process exit. The finally below calls it again, which is a no-op.
Invoke-CiTidy

# --- the record --------------------------------------------------------------
#: $recordDir itself is computed in the run-evidence block near the top, so the run
#: directory and the canonical record path cannot drift apart.
New-Item -ItemType Directory -Force -Path $recordDir | Out-Null
$verdict = if ($script:Failures.Count -eq 0) { 'PASS' } else { 'FAIL' }
$body = New-Object System.Collections.Generic.List[string]
$body.Add('local-ci record')
$body.Add('===============')
$body.Add("script_sha256  : " + (Get-FileHash -LiteralPath $PSCommandPath -Algorithm SHA256).Hash)
$body.Add("sha            : $Sha")
$body.Add("tree           : $tree")
$body.Add("subject        : $subject")
$body.Add("host           : $hostName, $cores logical cores, $totalGb GB RAM, $freeGb GB free at start")
$body.Add("workers        : $Workers")
$body.Add("timeout_seconds: $script:BudgetSeconds")
$body.Add("repo           : $RepoPath")
$body.Add("worktree       : $worktree (removed before this record was written)")
$body.Add("venv           : $venv")
$body.Add('')
$body.Add('steps')
$body.Add('-----')
foreach ($step in $script:Steps) { $body.Add(("  {0,-52} exit {1,-4} {2,8:N1}s" -f $step.Name, $step.Exit, $step.Seconds)) }
$body.Add('')
$body.Add('step captures (private, under ignored build/)')
$body.Add('------------------------------------------')
$body.Add(("  run            : {0}" -f $runId))
$body.Add(("  run directory  : {0}" -f $runDir.Substring($RepoPath.Length + 1)))
foreach ($step in $script:Steps) {
    foreach ($capture in $step.Captures) {
        $body.Add(("  {0,-46} {1} {2,10} byte(s)  {3}" -f $step.Name, $capture.Sha256, $capture.Bytes, $capture.Path))
    }
}
$body.Add('')
$body.Add('suite counts')
$body.Add('------------')
if ($junitCounts) {
    $body.Add(("  junit: tests={0} failures={1} errors={2} skipped={3}" -f $junitCounts.Tests, $junitCounts.Failures, $junitCounts.Errors, $junitCounts.Skipped))
} else { $body.Add('  junit: NOT AVAILABLE') }
$body.Add('')
$body.Add('per-file skipped versus the pinned CI figures')
$body.Add('-------------------------------------------')
$body.Add(("  pinned from trace job {0} at {1} (whole suite {2} skipped on Linux)" -f $PinnedTraceJob, $PinnedTraceSha.Substring(0, 8), $PinnedSuiteSkips))
if ($pinnedApplicable.Count -eq 0) { $body.Add('  pinned table NOT APPLICABLE at this SHA: no pinned file is present in the checkout') }
foreach ($file in $pinnedAbsent) { $body.Add(("  {0,-42} NOT PRESENT at this SHA, so not an equality gate" -f $file)) }
foreach ($file in ($pinnedApplicable | Sort-Object)) {
    $actual = 0
    if ($skipByFile.ContainsKey($file)) { $actual = $skipByFile[$file] }
    if ($hasPowerShellHost) {
        $body.Add(("  {0,-42} host has PowerShell, so not an equality gate (actual {1,3}, pinned {2,3})" -f $file, $actual, $PinnedSkips[$file]))
    } else {
        $body.Add(("  {0,-42} actual {1,3}  pinned {2,3}" -f $file, $actual, $PinnedSkips[$file]))
    }
}
$body.Add('')
$body.Add('  every file with a skip on this host:')
foreach ($file in ($skipByFile.Keys | Sort-Object)) { $body.Add(("    {0,-58} {1,3}" -f $file, $skipByFile[$file])) }
$body.Add('')
$body.Add('failing tests, by name (from the junit xml)')
$body.Add('------------------------------------------')
if ($failedCases.Count -eq 0) { $body.Add('  none') } else { foreach ($case in $failedCases) { $body.Add("  - $case") } }
$body.Add('')
$body.Add('peak memory')
$body.Add('-----------')
$body.Add(("  {0:N0} MB peak python tree, parent-pid tree walk during each step" -f ($script:PeakBytes / 1MB)))
$body.Add('  other work was running on the machine during this run')
$body.Add('')
$body.Add('failures')
$body.Add('--------')
if ($script:Failures.Count -eq 0) { $body.Add('  none') } else { foreach ($failure in $script:Failures) { $body.Add("  - $failure") } }
$body.Add('')
$body.Add('notes')
$body.Add('-----')
foreach ($note in $script:Notes) { $body.Add("  - $note") }
$body.Add('')
$body.Add('digest')
$body.Add('------')
$body.Add('  the sha256 below covers every byte of this file ABOVE this line')
$body.Add('')
$body.Add("verdict        : $verdict")

$text = ($body -join [Environment]::NewLine) + [Environment]::NewLine
$recordPath = Join-Path $recordDir 'record.txt'
$utf8 = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($recordPath, $text, $utf8)
$digest = (Get-FileHash -LiteralPath $recordPath -Algorithm SHA256).Hash
[System.IO.File]::WriteAllText((Join-Path $recordDir 'record.sha256'), $digest + [Environment]::NewLine, $utf8)
#: A copy inside this run's own directory: the next run writes the canonical path again,
#: and this run's evidence must survive that.
[System.IO.File]::WriteAllText((Join-Path $runDir 'record.txt'), $text, $utf8)
[System.IO.File]::WriteAllText((Join-Path $runDir 'record.sha256'), $digest + [Environment]::NewLine, $utf8)

} finally {
    Invoke-CiTidy
}

Write-Log ("record: $recordPath")
Write-Log ("digest: $digest")
if ($script:Failures.Count -eq 0) { Write-Host 'local-ci: PASS'; exit 0 }
Write-Host 'local-ci: FAIL'
foreach ($failure in $script:Failures) { Write-Host ("  - " + $failure) }
exit 1
