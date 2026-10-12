# local-ci.ps1 - a local full-CI record for one SHA.
#
# WHY THIS EXISTS: GitLab is over its CI-minutes quota and, measured 2026-10-12,
# creates ZERO jobs for a pipeline whose jobs all route to the self-hosted runner
# (probe pipeline 2940414636: 0 jobs, started_at null, no YAML error). So the
# GitLab pipeline cannot be the gate for a while. A record produced by this script
# on an exact SHA is the temporary substitute: it checks the SHA out as a linked
# worktree, builds a fresh environment, runs the same gates the CI jobs run, and
# writes a machine-checkable record. The GitLab pipeline takes over again the
# moment it can be created.
#
# The checkout is a LINKED WORKTREE, not a plain clone. Measured: in a plain clone
# tests/unit/test_pre_merge_check.py::test_the_primary_a_subdirectory_of_it_and_a_linked_worktree
# FAILS, because the gate correctly runs in a clone (a clone is not a linked
# worktree) while the test asserts the linked shape it has. That false failure
# cost one measurement round.
#
# USE:
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\local-ci.ps1 -Sha <40-hex> [-Workers N]
#
# -Workers defaults to 4 and is clamped to at most half the logical cores, because
# measured: at 8 workers on this 8-core machine the platform WMI query inside
# xdist workers raised a fatal 0x8007000e (E_OUTOFMEMORY) while other work held
# the box, and a 4-worker run of the same suite peaked at 2,862 MB across 12
# python processes.
#
# Everything fails closed: any non-zero step, a collapsed adjacency run, a pinned
# skip count that disagrees, JUnit disagreeing with the summary, a missing
# report.xml, or the 45-minute budget. No secrets, no network except pip.

[CmdletBinding()]
param(
    # The full 40-character commit SHA to record.
    [Parameter(Mandatory = $true)]
    [string]$Sha,

    # xdist worker count. Default 4; never more than half the logical cores.
    [int]$Workers = 4,

    # The repository the throwaway worktree is added from. Defaults to this
    # script's own repository, which is the one under review.
    [string]$RepoPath,

    # Pinned per-file skip figures. Default EMPTY on purpose: a baseline recorded
    # on one tree is not this tree's. The known Linux example, kept for the
    # record, is job 17122705022 at 43741b70 (test-sdk, 5194 passed, 314 skipped,
    # 0 failed, on a tree identical to the current master). When a file IS pinned
    # and IS present in the checkout its skip count is an equality gate; a pinned
    # file absent from the checkout is recorded as not applicable, never a
    # failure, because an absent file cannot legitimately skip anything.
    [hashtable]$PinnedSkips = @{},

    # The job the Linux figures in the record come from, recorded with them.
    [string]$PinnedTraceJob = '17122705022',
    [string]$PinnedTraceSha = '43741b704d1cb1b95ef29a69ae1970e857ae130d',

    # The Linux whole-suite skip count for the same tree, recorded for contrast.
    [int]$PinnedSuiteSkips = 314
)

$ErrorActionPreference = 'Stop'
$script:BudgetMinutes = 45
$script:Stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
$script:Steps = New-Object System.Collections.Generic.List[object]
$script:Failures = New-Object System.Collections.Generic.List[string]
$script:Notes = New-Object System.Collections.Generic.List[string]

if (-not $RepoPath) {
    $RepoPath = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
}

function Write-Log {
    param([string]$Text)
    Write-Host ("[{0,7:N1}s] {1}" -f $script:Stopwatch.Elapsed.TotalSeconds, $Text)
}

function Add-Failure {
    param([string]$Text)
    $script:Failures.Add($Text)
    Write-Log ("FAIL: $Text")
}

function Test-Budget {
    if ($script:Stopwatch.Elapsed.TotalMinutes -ge $script:BudgetMinutes) {
        Add-Failure ("the {0}-minute budget expired" -f $script:BudgetMinutes)
        return $false
    }
    return $true
}

function Invoke-RecordedStep {
    param(
        [Parameter(Mandatory)][string]$Name,
        [Parameter(Mandatory)][scriptblock]$Body
    )
    if (-not (Test-Budget)) { return $null }
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $transcript = New-Object System.Collections.Generic.List[string]
    $code = 0
    try {
        & $Body 2>&1 | ForEach-Object {
            $line = $_.ToString()
            $transcript.Add($line)
            Write-Host $line
        }
        $code = $LASTEXITCODE
        if ($null -eq $code) { $code = 0 }
    } catch {
        $code = 1
        $transcript.Add("EXCEPTION: " + $_.Exception.Message)
        Write-Host ("EXCEPTION: " + $_.Exception.Message)
    }
    $sw.Stop()
    $entry = [pscustomobject]@{
        Name    = $Name
        Exit    = $code
        Seconds = [math]::Round($sw.Elapsed.TotalSeconds, 1)
        Output  = ($transcript -join [Environment]::NewLine)
    }
    $script:Steps.Add($entry)
    if ($code -ne 0) { Add-Failure ("step '{0}' exited {1}" -f $Name, $code) }
    return $entry
}

# --- the SHA ------------------------------------------------------------------
if ($Sha -notmatch '^[0-9a-f]{40}$') {
    Write-Host "local-ci: FAIL - -Sha must be a full 40-character lowercase hex SHA, got '$Sha'"
    exit 1
}
Push-Location $RepoPath
$resolved = (& git rev-parse --verify --quiet "$Sha~0" 2>$null)
$resolved = if ($resolved) { $resolved.ToString().Trim() } else { $null }
Pop-Location
if (-not $resolved -or $resolved -ne $Sha) {
    Write-Host "local-ci: FAIL - $Sha does not resolve to itself in $RepoPath"
    exit 1
}

# --- host and memory ---------------------------------------------------------
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
Write-Log ("host {0}: {1} cores, {2} GB RAM, {3} GB free; workers {4}" -f $hostName, $cores, $totalGb, $freeGb, $Workers)

# --- the throwaway linked worktree -------------------------------------------
$sha8 = $Sha.Substring(0, 8)
$worktree = Join-Path $env:TEMP ("local-ci-" + $sha8)
if (Test-Path -LiteralPath $worktree) {
    Write-Log "removing a leftover worktree at $worktree"
    & git -C $RepoPath worktree remove --force $worktree 2>&1 | Out-Null
    if (Test-Path -LiteralPath $worktree) { Remove-Item -LiteralPath $worktree -Recurse -Force -ErrorAction SilentlyContinue }
}
Push-Location $RepoPath
& git worktree add --detach $worktree $Sha 2>&1 | ForEach-Object { Write-Host $_ }
$addCode = $LASTEXITCODE
Pop-Location
if ($addCode -ne 0 -or -not (Test-Path -LiteralPath $worktree)) {
    Write-Host "local-ci: FAIL - could not add a worktree at $worktree for $Sha"
    exit 1
}
$tree = (& git -C $worktree rev-parse HEAD).ToString().Trim()
$tree = (& git -C $worktree log -n 1 --format=%T $Sha).ToString().Trim()
Write-Log "worktree $worktree at $Sha (tree $tree)"

# --- the fresh venv ----------------------------------------------------------
$venv = Join-Path $env:LOCALAPPDATA ("log1-ci\local-ci-" + $sha8)
$venvPython = Join-Path $venv 'Scripts\python.exe'
$installTarget = $worktree + '[dev,workbench,research]'
$null = Invoke-RecordedStep -Name 'venv+install' -Body {
    if (Test-Path -LiteralPath $venv) { Remove-Item -LiteralPath $venv -Recurse -Force }
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $venv) | Out-Null
    & python -m venv $venv
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    & $venvPython -m pip install --quiet --disable-pip-version-check --upgrade pip
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    Push-Location $worktree
    & $venvPython -m pip install --quiet --disable-pip-version-check -e $installTarget
    $c = $LASTEXITCODE
    Pop-Location
    exit $c
}
if (-not (Test-Path -LiteralPath $venvPython)) {
    Write-Host "local-ci: FAIL - no interpreter at $venvPython after the install step"
    & git -C $RepoPath worktree remove --force $worktree 2>&1 | Out-Null
    exit 1
}
$env:QT_QPA_PLATFORM = 'offscreen'
$env:CLOUDFLARE_API_TOKEN = ''
$env:PYTEST_DEBUG_TEMPROOT = 'C:\Users\hears\AppData\Local\Temp\pytest-root'
$report = Join-Path $worktree 'report.xml'

# --- peak memory, sampled by process tree ------------------------------------
# A venv python.exe is a launcher stub, so xdist workers run under the BASE
# interpreter and a command-line filter misses them. Only the parent-pid tree walk
# sees them; measured peak on a 4-worker run was 2,862 MB across 12 processes.
$stopFile = Join-Path $env:TEMP ("local-ci-sampler-" + $sha8)
if (Test-Path -LiteralPath $stopFile) { Remove-Item -LiteralPath $stopFile -Force }
$sampler = Start-Job -ScriptBlock {
    param($worktreePath, $stopPath)
    $peak = 0; $peakProcs = 0; $samples = 0
    while (-not (Test-Path -LiteralPath $stopPath)) {
        $all = Get-CimInstance Win32_Process -Filter "Name = 'python.exe'" -ErrorAction SilentlyContinue |
            Select-Object ProcessId, ParentProcessId, CommandLine
        $roots = @($all | Where-Object { $_.CommandLine -and $_.CommandLine -like "*$worktreePath*" } | Select-Object -ExpandProperty ProcessId)
        $ids = New-Object System.Collections.Generic.HashSet[int]
        foreach ($r in $roots) { $null = $ids.Add([int]$r) }
        $changed = $true
        while ($changed) {
            $changed = $false
            foreach ($p in $all) {
                if ($ids.Contains([int]$p.ParentProcessId) -and -not $ids.Contains([int]$p.ProcessId)) {
                    $null = $ids.Add([int]$p.ProcessId); $changed = $true
                }
            }
        }
        $now = 0; $n = 0
        foreach ($id in $ids) {
            $ws = (Get-Process -Id $id -ErrorAction SilentlyContinue).WorkingSet64
            if ($ws) { $now += $ws; $n++ }
        }
        if ($now -gt $peak) { $peak = $now; $peakProcs = $n }
        $samples++
        Start-Sleep -Milliseconds 500
    }
    return [pscustomobject]@{ Peak = $peak; PeakProcs = $peakProcs; Samples = $samples }
} -ArgumentList $worktree, $stopFile

# --- steps -------------------------------------------------------------------
foreach ($quality in @('public_surface', 'architecture', 'public_release', 'readability')) {
    $captured = @('-m', ('tools.quality.' + $quality))
    if ($quality -eq 'public_surface' -or $quality -eq 'readability') { $captured += '--all' }
    $null = Invoke-RecordedStep -Name $quality -Body {
        Push-Location $worktree
        & $venvPython @captured
        $c = $LASTEXITCODE
        Pop-Location
        exit $c
    }
}

$pytestStep = Invoke-RecordedStep -Name ("pytest -n " + $Workers) -Body {
    Push-Location $worktree
    & $venvPython -m pytest tests/unit -q --dist loadfile -n $Workers --junitxml=report.xml
    $c = $LASTEXITCODE
    Pop-Location
    exit $c
}

foreach ($order in @('forward', 'reverse')) {
    $capturedOrder = $order
    $null = Invoke-RecordedStep -Name ("adjacency " + $order) -Body {
        Push-Location $worktree
        & $venvPython -m scripts.adjacency_run -Order $capturedOrder
        $c = $LASTEXITCODE
        Pop-Location
        exit $c
    }
}

$null = Invoke-RecordedStep -Name 'test-integration selection' -Body {
    Push-Location $worktree
    & $venvPython -m pytest tests/integration/test_container_decode_synthetic.py -q
    $c = $LASTEXITCODE
    Pop-Location
    exit $c
}

# stop the sampler
New-Item -ItemType File -Path $stopFile -Force | Out-Null
$sample = Receive-Job -Job $sampler -Wait
Remove-Job -Job $sampler -Force
$peakBytes = 0; $peakProcs = 0; $memorySamples = 0
if ($sample) { $peakBytes = $sample.Peak; $peakProcs = $sample.PeakProcs; $memorySamples = $sample.Samples }
Remove-Item -LiteralPath $stopFile -Force -ErrorAction SilentlyContinue

# --- adjacency completeness --------------------------------------------------
foreach ($order in @('forward', 'reverse')) {
    $name = "adjacency " + $order
    $step = $script:Steps | Where-Object { $_.Name -eq $name } | Select-Object -First 1
    if (-not $step) { Add-Failure ("no record for $name"); continue }
    if ($step.Exit -ne 0) { continue }
    if ($step.Output -match 'ran\s+\d+\s+modules\s+clean') { continue }
    if ($step.Output -match 'modules' -and $step.Output -match 'clean') {
        $script:Notes.Add("$name reported its clean run in an unrecognised wording; matched 'modules' and 'clean'")
        continue
    }
    Add-Failure ("$name did not report a clean module run")
}

# --- skip counts against the pinned CI figures -------------------------------
$skipByFile = @{}
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
        if ($case.skipped) {
            $file = $case.file
            if (-not $file) { $file = ($case.classname -replace '\.', '/') }
            if ($file) {
                if ($skipByFile.ContainsKey($file)) { $skipByFile[$file]++ } else { $skipByFile[$file] = 1 }
            }
        }
    }
} else {
    Add-Failure 'report.xml is missing, so the suite produced no machine-checkable result'
}

if ($junitCounts -and $pytestStep) {
    if ($pytestStep.Output -match '(\d+) skipped') {
        $summarySkips = [int]$Matches[1]
        if ($summarySkips -ne $junitCounts.Skipped) {
            Add-Failure ("summary says $summarySkips skipped, junit says $($junitCounts.Skipped)")
        }
    }
    if ($junitCounts.Failures -gt 0 -or $junitCounts.Errors -gt 0) {
        Add-Failure ("junit reports {0} failures and {1} errors" -f $junitCounts.Failures, $junitCounts.Errors)
    }
}

$pinnedApplicable = New-Object System.Collections.Generic.List[string]
$pinnedAbsent = New-Object System.Collections.Generic.List[string]
foreach ($file in $PinnedSkips.Keys) {
    $expected = $PinnedSkips[$file]
    if (-not (Test-Path -LiteralPath (Join-Path $worktree $file))) {
        $pinnedAbsent.Add($file)
        continue
    }
    $pinnedApplicable.Add($file)
    $actual = 0
    if ($skipByFile.ContainsKey($file)) { $actual = $skipByFile[$file] }
    if ($actual -ne $expected) {
        Add-Failure ("$file skipped $actual, pinned $expected from the CI trace job $PinnedTraceJob at $($PinnedTraceSha.Substring(0,8))")
    }
}

# --- the record --------------------------------------------------------------
$recordDir = Join-Path (Join-Path $RepoPath 'build') (Join-Path 'local-ci' $Sha)
New-Item -ItemType Directory -Force -Path $recordDir | Out-Null
$verdict = if ($script:Failures.Count -eq 0) { 'PASS' } else { 'FAIL' }
$body = New-Object System.Collections.Generic.List[string]
$body.Add("local-ci record")
$body.Add("===============")
$body.Add("sha            : $Sha")
$body.Add("tree           : $tree")
$body.Add("host           : $hostName, $cores logical cores, $totalGb GB RAM, $freeGb GB free at start")
$body.Add("workers        : $Workers")
$body.Add("repo           : $RepoPath")
$body.Add("worktree       : $worktree (removed at the end of this run)")
$body.Add("venv           : $venv")
$body.Add("budget         : $script:BudgetMinutes minutes")
$body.Add("")
$body.Add("steps")
$body.Add("-----")
foreach ($step in $script:Steps) {
    $body.Add(("  {0,-30} exit {1,-3} {2,8:N1}s" -f $step.Name, $step.Exit, $step.Seconds))
}
$body.Add("")
$body.Add("suite counts")
$body.Add("------------")
if ($junitCounts) {
    $body.Add(("  junit: tests={0} failures={1} errors={2} skipped={3}" -f $junitCounts.Tests, $junitCounts.Failures, $junitCounts.Errors, $junitCounts.Skipped))
    $body.Add(("  linux baseline for the same tree: job {0} at {1}, {2} skipped, 0 failed" -f $PinnedTraceJob, $PinnedTraceSha.Substring(0, 8), $PinnedSuiteSkips))
    $body.Add(("  windows minus linux skipped: {0}" -f ($junitCounts.Skipped - $PinnedSuiteSkips)))
} else {
    $body.Add("  junit: NOT AVAILABLE (report.xml missing)")
}
$body.Add("")
$body.Add("per-file skipped versus the pinned CI figures")
$body.Add("-------------------------------------------")
if ($pinnedApplicable.Count -eq 0) {
    $body.Add("  pinned table NOT APPLICABLE at this SHA: no pinned file is present in the checkout")
}
foreach ($file in $pinnedAbsent) {
    $body.Add(("  {0,-42} NOT PRESENT at this SHA, so not an equality gate" -f $file))
}
foreach ($file in ($pinnedApplicable | Sort-Object)) {
    $actual = 0
    if ($skipByFile.ContainsKey($file)) { $actual = $skipByFile[$file] }
    $body.Add(("  {0,-42} actual {1,3}  pinned {2,3}" -f $file, $actual, $PinnedSkips[$file]))
}
$body.Add("")
$body.Add("  every file with a skip on this host:")
foreach ($file in ($skipByFile.Keys | Sort-Object)) {
    $body.Add(("    {0,-58} {1,3}" -f $file, $skipByFile[$file]))
}
$body.Add("")
$body.Add("peak memory")
$body.Add("-----------")
$body.Add(("  {0:N0} MB across {1} python processes, {2} samples, parent-pid tree walk" -f ($peakBytes / 1MB), $peakProcs, $memorySamples))
$body.Add("  the machine also ran agent sessions during this run")
$body.Add("")
$body.Add("failures")
$body.Add("--------")
if ($script:Failures.Count -eq 0) {
    $body.Add("  none")
} else {
    foreach ($failure in $script:Failures) { $body.Add("  - $failure") }
}
$body.Add("")
$body.Add("notes")
$body.Add("-----")
foreach ($note in $script:Notes) { $body.Add("  - $note") }
$body.Add("")
$body.Add("digest")
$body.Add("------")
$body.Add("  the sha256 below covers every byte of this file ABOVE this line")
$body.Add("")
$body.Add("verdict        : $verdict")

$text = ($body -join [Environment]::NewLine) + [Environment]::NewLine
$recordPath = Join-Path $recordDir 'record.txt'
$utf8 = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($recordPath, $text, $utf8)
$digest = (Get-FileHash -LiteralPath $recordPath -Algorithm SHA256).Hash
[System.IO.File]::WriteAllText((Join-Path $recordDir 'record.sha256'), $digest + [Environment]::NewLine, $utf8)

# --- tidy the worktree -------------------------------------------------------
Push-Location $RepoPath
& git worktree remove --force $worktree 2>&1 | ForEach-Object { Write-Host $_ }
$removed = -not (Test-Path -LiteralPath $worktree)
Pop-Location
if (-not $removed) { Add-Failure 'the throwaway worktree could not be removed' }
Write-Log ("worktree removed: {0}" -f $removed)

Write-Log ("record: $recordPath")
Write-Log ("digest: $digest")
if ($script:Failures.Count -eq 0) {
    Write-Host 'local-ci: PASS'
    exit 0
}
Write-Host 'local-ci: FAIL'
foreach ($failure in $script:Failures) { Write-Host ("  - " + $failure) }
exit 1
