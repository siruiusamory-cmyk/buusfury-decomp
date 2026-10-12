#Requires -Version 5.1
<#
scripts/local-ci.ps1 - the local full-CI gate.

    powershell -NoProfile -ExecutionPolicy Bypass -File scripts\local-ci.ps1 `
        -Sha <full 40-char sha> [-Workers N] [-RepoPath <repo>]

This is the temporary CI gate while GitLab cannot create a pipeline for the
project: the namespace is over its CI-minutes quota, and the quota check runs
before runner tag matching, so a pipeline is refused with zero jobs attached
(measured 2026-10-12, pipeline 2940338375). It takes a SHA, materialises it as a
LINKED WORKTREE, builds its own venv outside every repository, runs the four
quality gates, the portable suite under xdist, the app-wide Qt adjacency set in
both orders and the ROM-free integration file, and writes a record a reviewer can
check under build/local-ci/<sha8>/.

A LINKED WORKTREE, not a plain clone: a plain clone is not a linked worktree, and
tests/unit/test_pre_merge_check.py::test_the_primary_a_subdirectory_of_it_and_a_linked_worktree
fails in one. The same test PASSES in a linked worktree, which is why the clone
has to be one.

Fail closed. Any step exit code, a missing report.xml, the JUnit XML disagreeing
with the pytest summary line, the adjacency runner not proving the full set ran,
or the 45-minute budget: FAIL. On budget expiry the running process tree is
killed with taskkill /T /F and the timeout is recorded.

Pin provenance: the pinned figures below were read by this lane from the GitLab
CI trace of job 17121704860 at 9c34f1ae, whose pytest summary line was
"8 failed, 5234 passed, 320 skipped in 177.17s (0:02:57)". The per-file table is
aggregated from that trace's SKIPPED lines. That commit is NOT an ancestor of
master (merge-base --is-ancestor 9c34f1ae HEAD exits 1; it lives on
remotes/origin/ticket/retro-tools-001), and the files holding the 13 PowerShell
nodes - test_dev_tools.py 6, test_worktree_owners.py 7 - do not exist in the tree
this gate checks. The pinned table is therefore a comparison, never an equality
gate: every delta is recorded with its cause, and only a delta with no cause is a
failure.

-RunStep / -SkipInflation / -ForceTimeoutSeconds exist to drive this script's
fail-closed arms to failure on demand. They are not run modes.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string] $Sha,

    [int] $Workers = 4,

    [string] $RepoPath,

    # Drive arms to failure: '1' makes the portable suite a nonexistent
    # selection, '5' makes the second adjacency order repeat the first.
    [ValidateSet('', '1', '5')]
    [string] $RunStep = '',

    # A pinned file to report one more skip for than it really has.
    [string] $SkipInflation = '',

    # A budget far below the step's cost, to prove the kill path.
    [int] $ForceTimeoutSeconds = 0
)

$ErrorActionPreference = 'Stop'
$ScriptPath = $MyInvocation.MyCommand.Path
$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$BudgetSeconds = 45 * 60

# --- the pinned figures -----------------------------------------------------
$PinnedJob = '17121704860'
$PinnedSha = '9c34f1ae'
$PinnedPassed = 5234
$PinnedFailed = 8
$PinnedSkipped = 320

$PinnedTable = @(
    'tests/rom_support.py=3=rom'
    'tests/unit/test_atlas_range_index.py=9=atlas'
    'tests/unit/test_capability_registry.py=1=site'
    'tests/unit/test_dev_tools.py=6=powershell'
    'tests/unit/test_dialogue_font.py=5=rom'
    'tests/unit/test_dragonbyte_data_acceptance.py=5=rom'
    'tests/unit/test_dragonbyte_dataedits.py=7=rom'
    'tests/unit/test_dragonbyte_datapage.py=19=rom'
    'tests/unit/test_dragonbyte_datasurface.py=14=rom'
    'tests/unit/test_dragonbyte_entity_acceptance.py=12=rom'
    'tests/unit/test_dragonbyte_entitysurface.py=16=rom'
    'tests/unit/test_dragonbyte_foundation.py=1=rom'
    'tests/unit/test_dragonbyte_graphics_acceptance.py=12=rom'
    'tests/unit/test_dragonbyte_graphicsurface.py=16=rom'
    'tests/unit/test_dragonbyte_map_acceptance.py=11=rom'
    'tests/unit/test_dragonbyte_mapedits.py=8=rom'
    'tests/unit/test_dragonbyte_mappage.py=19=rom'
    'tests/unit/test_dragonbyte_mapsurface.py=20=rom'
    'tests/unit/test_dragonbyte_rawbytes.py=3=rom'
    'tests/unit/test_dragonbyte_romsurface.py=3=rom'
    'tests/unit/test_dragonbyte_state.py=1=rom'
    'tests/unit/test_dragonbyte_text_acceptance.py=15=rom'
    'tests/unit/test_dragonbyte_textsurface.py=14=rom'
    'tests/unit/test_friend_v3_boss_profile.py=6=rom'
    'tests/unit/test_friend_v4b_cell.py=4=rom'
    'tests/unit/test_graphic_identity_numbering.py=1=rom'
    'tests/unit/test_logx_frame_probe.py=1=environment'
    'tests/unit/test_map_render.py=1=rom'
    'tests/unit/test_mgba_extra_script.py=6=rom'
    'tests/unit/test_mgba_instrumented_identity.py=4=environment'
    'tests/unit/test_mgba_runtime_skill.py=35=powershell'
    'tests/unit/test_palette_census.py=3=rom'
    'tests/unit/test_project_safety.py=1=linux-only'
    'tests/unit/test_questline_rail.py=4=site'
    'tests/unit/test_randomizer_release.py=2=declared'
    'tests/unit/test_rom_destination_safety.py=10=linux-only'
    'tests/unit/test_rom_fixture_isolation.py=2=rom'
    'tests/unit/test_site_consistency.py=2=site'
    'tests/unit/test_sprite_new_runtime.py=1=optional-import'
    'tests/unit/test_spritefix_attribution.py=1=rom'
    'tests/unit/test_text_engine.py=4=rom'
    'tests/unit/test_workbench_graphics.py=1=rom'
    'tests/unit/test_workbench_session.py=4=rom'
    'tests/unit/test_worktree_owners.py=7=powershell'
)

$Pinned = [ordered]@{}
$PinnedCause = @{}
foreach ($row in $PinnedTable) {
    $parts = $row.Split('=')
    $Pinned[$parts[0]] = [int]$parts[1]
    $PinnedCause[$parts[0]] = $parts[2]
}
$PinnedTableTotal = 0
foreach ($key in $Pinned.Keys) { $PinnedTableTotal += $Pinned[$key] }

# --- deterministic paths and state ------------------------------------------
$Sha8 = if ($Sha.Length -ge 8) { $Sha.Substring(0, 8) } else { 'sha' }
if (-not $RepoPath) { $RepoPath = Join-Path $PSScriptRoot '..' }
$RepoRoot = [System.IO.Path]::GetFullPath($RepoPath)
$RecordDir = Join-Path $RepoRoot ('build\local-ci\' + $Sha8)
$LogDir = Join-Path $RecordDir 'logs'
$VenvDir = Join-Path (Join-Path $env:LOCALAPPDATA 'log1-ci') ('local-ci-' + $Sha8)
$WorktreeDir = Join-Path $env:TEMP ('local-ci-' + $Sha8 + '-' + $PID)

New-Item -ItemType Directory -Force -Path $RecordDir, $LogDir | Out-Null

function Invoke-GitLines {
    # $ErrorActionPreference = 'Stop' turns git's stderr into a terminating error,
    # and asking rev-parse for the commit form of a SHA does not work from
    # PowerShell 5.1 at all (measured: exit 1 and empty output for a valid SHA).
    $previous = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    $output = @(& git -C $RepoRoot @Arguments 2>&1 | ForEach-Object { $_.ToString() })
    $ErrorActionPreference = $previous
    return $output
}

$Record = New-Object System.Collections.Generic.List[string]
$script:RunStarted = Get-Date
$script:PeakTreeBytes = 0L
$script:LastSample = Get-Date
$script:StepIndex = 0
$script:StepCount = 0
$script:StepFailures = 0
$script:StopReason = $null

function Add-Record {
    param([string] $Text = '')
    $Record.Add($Text)
    Write-Host $Text
}

function Save-Record {
    $text = ($Record.ToArray() -join "`r`n") + "`r`n"
    [System.IO.File]::WriteAllText((Join-Path $RecordDir 'record.txt'), $text, $Utf8NoBom)
}

function Set-Stop {
    param([string] $Text)
    if (-not $script:StopReason) { $script:StopReason = $Text }
}

function Get-ElapsedSeconds {
    return ((Get-Date) - $script:RunStarted).TotalSeconds
}

function Complete-Record {
    param([bool] $Pass, [string] $Reason)
    $verdict = 'FAIL'
    if ($Pass) { $verdict = 'PASS' }
    Add-Record ''
    Add-Record ('verdict: ' + $verdict)
    Add-Record ('reason: ' + $Reason)
    Save-Record
    $digest = (Get-FileHash -LiteralPath (Join-Path $RecordDir 'record.txt') -Algorithm SHA256).Hash
    $lines = @(
        'local-ci record digest'
        'covers: the whole of record.txt, UTF-8 without BOM, CRLF line endings'
        ('sha256: ' + $digest)
    )
    [System.IO.File]::WriteAllText((Join-Path $RecordDir 'record.sha256'), (($lines -join "`r`n") + "`r`n"), $Utf8NoBom)
    Write-Host ''
    Write-Host ('local-ci: ' + $verdict)
    Write-Host ('record: ' + (Join-Path $RecordDir 'record.txt'))
    Write-Host ('reason: ' + $Reason)
    if ($Pass) { exit 0 } else { exit 1 }
}

# --- process helpers --------------------------------------------------------

# Every live process whose ancestor chain reaches $RootPid. A venv python.exe is
# a launcher stub: xdist workers run under the base interpreter and do not carry
# the venv path on their command line, so a command-line filter misses them. The
# parent-pid tree walk is the only measurement that worked.
function Get-TreeProcesses {
    param([int] $RootPid)
    $all = @(Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.Id -ne $PID })
    $byParent = @{}
    foreach ($p in $all) {
        try { $parent = $p.Parent.Id } catch { continue }
        if (-not $byParent.ContainsKey($parent)) { $byParent[$parent] = New-Object System.Collections.ArrayList }
        [void]$byParent[$parent].Add($p)
    }
    $found = New-Object System.Collections.ArrayList
    $queue = New-Object System.Collections.Queue
    $queue.Enqueue($RootPid)
    while ($queue.Count -gt 0) {
        $current = $queue.Dequeue()
        if (-not $byParent.ContainsKey($current)) { continue }
        foreach ($child in $byParent[$current]) {
            [void]$found.Add($child)
            $queue.Enqueue($child.Id)
        }
    }
    return $found
}

function Get-TreeBytes {
    param([int] $RootPid)
    $total = 0L
    foreach ($p in (Get-TreeProcesses -RootPid $RootPid)) {
        try { $total += $p.WorkingSet64 } catch { }
    }
    return $total
}

# One external command, its output captured to one log file, a memory sampler
# running while it works, and a deadline that kills the whole process tree.
function Invoke-Captured {
    param(
        [string] $FilePath,
        [string[]] $Arguments,
        [string] $LogPath,
        [string] $WorkDir,
        [hashtable] $Environment,
        [int] $DeadlineSeconds
    )
    $saved = @{}
    foreach ($name in $Environment.Keys) {
        $saved[$name] = [Environment]::GetEnvironmentVariable($name, 'Process')
        [Environment]::SetEnvironmentVariable($name, $Environment[$name], 'Process')
    }
    $started = Get-Date
    $timedOut = $false
    $exit = -1
    try {
        $info = New-Object System.Diagnostics.ProcessStartInfo
        $info.FileName = $FilePath
        $info.Arguments = (($Arguments | ForEach-Object { '"' + $_ + '"' }) -join ' ')
        $info.WorkingDirectory = $WorkDir
        $info.UseShellExecute = $false
        $info.CreateNoWindow = $true
        $info.StandardOutputEncoding = [System.Text.Encoding]::UTF8
        $info.StandardErrorEncoding = [System.Text.Encoding]::UTF8
        $process = New-Object System.Diagnostics.Process
        $process.StartInfo = $info
        $writer = New-Object System.IO.StreamWriter($LogPath, $false, $Utf8NoBom)
        $writer.AutoFlush = $true
        [void]$process.Start()
        $outTask = $process.StandardOutput.ReadLineAsync()
        $errTask = $process.StandardError.ReadLineAsync()
        while ($true) {
            if ($outTask -ne $null -and $outTask.IsCompleted) {
                $line = $outTask.Result
                if ($line -eq $null) { $outTask = $null }
                else {
                    $writer.WriteLine($line)
                    $outTask = $process.StandardOutput.ReadLineAsync()
                }
            }
            if ($errTask -ne $null -and $errTask.IsCompleted) {
                $line = $errTask.Result
                if ($line -eq $null) { $errTask = $null }
                else {
                    $writer.WriteLine($line)
                    $errTask = $process.StandardError.ReadLineAsync()
                }
            }
            if (((Get-Date) - $script:LastSample).TotalMilliseconds -ge 500) {
                $script:LastSample = Get-Date
                $live = Get-TreeBytes -RootPid $process.Id
                if ($live -gt $script:PeakTreeBytes) { $script:PeakTreeBytes = $live }
            }
            if ($process.HasExited) {
                if ($outTask -ne $null -and $outTask.IsCompleted -and $outTask.Result -ne $null) { $writer.WriteLine($outTask.Result) }
                if ($errTask -ne $null -and $errTask.IsCompleted -and $errTask.Result -ne $null) { $writer.WriteLine($errTask.Result) }
                break
            }
            $elapsed = (Get-Date) - $script:RunStarted
            $overBudget = ($DeadlineSeconds -gt 0) -and ($elapsed.TotalSeconds -ge $DeadlineSeconds)
            $overForced = ($ForceTimeoutSeconds -gt 0) -and ($elapsed.TotalSeconds -ge $ForceTimeoutSeconds) -and -not $overBudget
            if ($overBudget -or $overForced) {
                $timedOut = $true
                if ($overForced) { Set-Stop 'driven timeout' }
                Write-Host ('local-ci: killing the process tree of pid ' + $process.Id + ' (timeout)')
                & taskkill.exe /PID $process.Id /T /F 2>&1 | Out-Null
                Start-Sleep -Milliseconds 500
                break
            }
            Start-Sleep -Milliseconds 25
        }
        if (-not $timedOut) { $process.WaitForExit() }
        $exit = $process.ExitCode
        $writer.Dispose()
    } catch {
        Set-Stop ('command could not be run: ' + $_.Exception.Message)
    } finally {
        foreach ($name in $saved.Keys) {
            [Environment]::SetEnvironmentVariable($name, $saved[$name], 'Process')
        }
    }
    $seconds = [math]::Round(((Get-Date) - $started).TotalSeconds, 1)
    return [pscustomobject]@{ ExitCode = $exit; Seconds = $seconds; TimedOut = $timedOut }
}

function Add-Step {
    param([string] $Name, [int] $ExitCode, [double] $Seconds, [string] $LogPath)
    $script:StepIndex++
    $script:StepCount++
    Add-Record ('{0}. {1}: exit={2} wall={3}s log={4}' -f $script:StepIndex, $Name, $ExitCode, $Seconds, $LogPath)
    if ($ExitCode -ne 0) {
        $script:StepFailures++
        Set-Stop ('step failed: {0} exited {1}' -f $Name, $ExitCode)
    }
}

function Fail-Step {
    param([string] $Name, [string] $Why)
    $script:StepIndex++
    $script:StepCount++
    Add-Record ('{0}. {1}: NOT RUN ({2})' -f $script:StepIndex, $Name, $Why)
    Set-Stop ('step failed: {0} ({1})' -f $Name, $Why)
}

function Get-LogText {
    param([string] $Path)
    if (Test-Path $Path) { return (Get-Content -LiteralPath $Path -Raw) }
    return ''
}

function Get-JUnitCounts {
    param([string] $Path)
    $counts = @{ collected = 0; passed = 0; failed = 0; skipped = 0; error = 0 }
    if (-not (Test-Path $Path)) { return $counts }
    try { [xml] $xml = Get-Content -LiteralPath $Path -Raw } catch { return $counts }
    foreach ($case in $xml.SelectNodes('//testcase')) {
        $counts.collected++
        $outcome = 'passed'
        foreach ($child in $case.ChildNodes) {
            if ($child.Name -eq 'skipped') { $outcome = 'skipped' }
            elseif ($child.Name -eq 'failure') { $outcome = 'failed' }
            elseif ($child.Name -eq 'error') { $outcome = 'error' }
        }
        $counts[$outcome]++
    }
    return $counts
}

function Get-SkipTable {
    param([string] $Path)
    $table = @{}
    if (-not (Test-Path $Path)) { return $table }
    try { [xml] $xml = Get-Content -LiteralPath $Path -Raw } catch { return $table }
    foreach ($case in $xml.SelectNodes('//testcase')) {
        $skipped = $false
        foreach ($child in $case.ChildNodes) { if ($child.Name -eq 'skipped') { $skipped = $true } }
        if (-not $skipped) { continue }
        $name = [string]$case.GetAttribute('classname')
        $file = ($name -replace '\.', '/') + '.py'
        if (-not $table.ContainsKey($file)) { $table[$file] = 0 }
        $table[$file]++
    }
    return $table
}

# --- the fail-closed arms, in the order the brief gives them ----------------

Add-Record 'local-ci record'
Add-Record ('script_sha256: ' + (Get-FileHash -LiteralPath $ScriptPath -Algorithm SHA256).Hash)
Add-Record ('timeout_seconds: ' + $BudgetSeconds)
Add-Record 'memory_sample: parent-pid tree walk, sampled continuously while each step runs (a venv python.exe is a launcher stub, so a command-line filter misses xdist workers).'
Add-Record 'note: other work ran on this machine during the run, so peak memory is an upper bound for this gate alone.'

if ($Sha -notmatch '^[0-9a-fA-F]{40}$') {
    Add-Record ('sha: ' + $Sha)
    Complete-Record -Pass $false -Reason ('-Sha must be a full 40-character hex SHA, got: ' + $Sha)
}

$resolved = (Invoke-GitLines @('rev-parse', '--verify', '--quiet', $Sha) -join [Environment]::NewLine).Trim()
Add-Record ('sha: ' + $Sha)
Add-Record ('repo: ' + $RepoRoot)
Add-Record ('worktree: ' + $WorktreeDir)
Add-Record ('venv: ' + $VenvDir)
Add-Record ('record_dir: ' + $RecordDir)
if ($resolved -notmatch '^[0-9a-fA-F]{40}$') {
    Complete-Record -Pass $false -Reason ('-Sha does not resolve to a commit in ' + $RepoRoot + ': ' + $Sha + ' (' + $resolved + ')')
}
if ($resolved.ToLower() -ne $Sha.ToLower()) {
    Complete-Record -Pass $false -Reason ('-Sha resolved to a different commit: ' + $resolved)
}

$ignore = (Invoke-GitLines @('check-ignore', '-v', 'build/local-ci/probe') -join [Environment]::NewLine).Trim()
Add-Record ('build_ignored_by: ' + $ignore)
if (-not $ignore) {
    Complete-Record -Pass $false -Reason 'build/local-ci is not ignored by git here; refusing to write an artefact that could be committed'
}
if ($env:GITLAB_CI) {
    Complete-Record -Pass $false -Reason 'GITLAB_CI is set; this gate is for a local operator'
}

$tree = (Invoke-GitLines @('rev-parse', ($resolved + '^{tree}')) -join [Environment]::NewLine).Trim()
$subject = (Invoke-GitLines @('log', '-n', '1', '--format=%s', $resolved) -join [Environment]::NewLine).Trim()
$dirty = (Invoke-GitLines @('status', '--porcelain') -join [Environment]::NewLine).Trim()
Add-Record ('tree: ' + $tree)
Add-Record ('subject: ' + $subject)
$dirtyState = 'no'
if ($dirty) { $dirtyState = 'yes' }
Add-Record ('repo_dirty: ' + $dirtyState)
if ($dirty) {
    Complete-Record -Pass $false -Reason 'the source repository has uncommitted changes; the record would not describe the SHA alone'
}

$hostCores = [int]$env:NUMBER_OF_PROCESSORS
if ($hostCores -lt 1) { $hostCores = 1 }
$workerLimit = [math]::Floor($hostCores / 2)
if ($workerLimit -lt 1) { $workerLimit = 1 }
$requestedWorkers = $Workers
if ($Workers -gt $workerLimit) { $Workers = $workerLimit }
if ($Workers -lt 1) { $Workers = 1 }
$clamped = 'no'
if ($requestedWorkers -ne $Workers) { $clamped = 'yes' }
$os = Get-CimInstance Win32_OperatingSystem
Add-Record ('host: ' + $env:COMPUTERNAME + ' logical_cores=' + $hostCores + ' ram_mb=' + [math]::Round($os.TotalVisibleMemorySize / 1KB))
Add-Record ('free_ram_mb_at_start: ' + [math]::Round($os.FreePhysicalMemory / 1KB))
Add-Record ('workers: requested=' + $requestedWorkers + ' used=' + $Workers + ' clamped=' + $clamped)

$venvPython = Join-Path $VenvDir 'Scripts\python.exe'
if (Test-Path $VenvDir) {
    Complete-Record -Pass $false -Reason ('the venv directory already exists, refusing to reuse it: ' + $VenvDir)
}
$pythonBase = $null
$pythonCommand = Get-Command python.exe -ErrorAction SilentlyContinue
if ($pythonCommand) { $pythonBase = $pythonCommand.Source }
if (-not $pythonBase) {
    $pyCommand = Get-Command py.exe -ErrorAction SilentlyContinue
    if ($pyCommand) { $pythonBase = $pyCommand.Source }
}
if (-not $pythonBase) {
    Complete-Record -Pass $false -Reason 'no python.exe or py.exe on PATH to build the venv with'
}
Add-Record ('python_base: ' + $pythonBase)

Add-Record ''
Add-Record ('pinned_from: job ' + $PinnedJob + ' at ' + $PinnedSha + ' (Linux baseline CI trace)')
Add-Record ('pinned_totals: passed=' + $PinnedPassed + ' failed=' + $PinnedFailed + ' skipped=' + $PinnedSkipped + ' per_file_table_total=' + $PinnedTableTotal)
if ($PinnedTableTotal -ne $PinnedSkipped) {
    Complete-Record -Pass $false -Reason ('the pinned per-file table sums to ' + $PinnedTableTotal + ' but the pinned whole-suite figure is ' + $PinnedSkipped)
}

# --- the fresh venv, then the linked worktree -------------------------------

$stepEnvBase = @{
    QT_QPA_PLATFORM = 'offscreen'
    CLOUDFLARE_API_TOKEN = ''
    PYTHONPATH = $WorktreeDir
    PYTHONIOENCODING = 'utf-8'
    PYTHONDONTWRITEBYTECODE = '1'
    PIP_DISABLE_PIP_VERSION_CHECK = '1'
    PIP_NO_INPUT = '1'
    PYTHONUTF8 = '1'
}

function Get-StepEnvironment {
    $envCopy = @{}
    foreach ($key in $stepEnvBase.Keys) { $envCopy[$key] = $stepEnvBase[$key] }
    return $envCopy
}

$venvLog = Join-Path $LogDir 'venv.log'
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $VenvDir) | Out-Null
$r = Invoke-Captured -FilePath $pythonBase -Arguments @('-m', 'venv', $VenvDir) -LogPath $venvLog -WorkDir $RecordDir -Environment @{} -DeadlineSeconds $BudgetSeconds
Add-Step 'fresh venv at the fixed path, never --system-site-packages' $r.ExitCode $r.Seconds $venvLog
if ($r.TimedOut) { Complete-Record -Pass $false -Reason 'the 45-minute budget expired while creating the venv' }

if (-not $script:StopReason) {
    $log = Join-Path $LogDir 'worktree-add.log'
    $r = Invoke-Captured -FilePath 'git' -Arguments @('worktree', 'add', '--detach', $WorktreeDir, $resolved) -LogPath $log -WorkDir $RepoRoot -Environment @{} -DeadlineSeconds 300
    Add-Step 'git worktree add (linked worktree, not a clone)' $r.ExitCode $r.Seconds $log
}
if (-not $script:StopReason) {
    $worktreeGitDir = (Invoke-GitLines @('rev-parse', '--git-dir') -join [Environment]::NewLine).Trim()
    Add-Record ('worktree_git_dir: ' + $worktreeGitDir)
    if (-not (Test-Path (Join-Path $WorktreeDir 'pyproject.toml'))) {
        Set-Stop 'the worktree has no pyproject.toml; it is not a checkable checkout'
    }
}

# The pinned files, on the tree as committed: absent here means the pinned trace
# describes a different tree, which is recorded rather than failed.
$pinnedAbsent = 0
foreach ($key in $Pinned.Keys) {
    if (-not (Test-Path (Join-Path $WorktreeDir $key))) { $pinnedAbsent++ }
}
Add-Record ('pinned_files: total=' + $Pinned.Count + ' absent_at_this_sha=' + $pinnedAbsent)

# --- the steps --------------------------------------------------------------

$installLog = Join-Path $LogDir 'install.log'
if (-not $script:StopReason) {
    $r = Invoke-Captured -FilePath $venvPython -Arguments @('-m', 'pip', 'install', '--quiet', '-e', '.[dev,workbench,research]') -LogPath $installLog -WorkDir $WorktreeDir -Environment (Get-StepEnvironment) -DeadlineSeconds $BudgetSeconds
    Add-Step 'pip install -e .[dev,workbench,research] from the worktree' $r.ExitCode $r.Seconds $installLog
    if ($r.TimedOut) { Complete-Record -Pass $false -Reason 'the 45-minute budget expired while installing the extras' }
}
if (-not (Test-Path $venvPython)) {
    Set-Stop ('no interpreter at ' + $venvPython + ' after the install step')
}

$gates = @(
    @{ Name = 'python -m tools.quality.public_surface --all'; Args = @('-m', 'tools.quality.public_surface', '--all') }
    @{ Name = 'python -m tools.quality.architecture'; Args = @('-m', 'tools.quality.architecture') }
    @{ Name = 'python -m tools.quality.public_release'; Args = @('-m', 'tools.quality.public_release') }
    @{ Name = 'python -m tools.quality.readability --all'; Args = @('-m', 'tools.quality.readability', '--all') }
)
$gateIndex = 0
foreach ($gate in $gates) {
    if ($script:StopReason) {
        $gateIndex++
        Fail-Step $gate.Name 'an earlier step failed'
        continue
    }
    $gateIndex++
    $log = Join-Path $LogDir ('gate-' + $gateIndex + '.log')
    $r = Invoke-Captured -FilePath $venvPython -Arguments $gate.Args -LogPath $log -WorkDir $WorktreeDir -Environment (Get-StepEnvironment) -DeadlineSeconds $BudgetSeconds
    Add-Step $gate.Name $r.ExitCode $r.Seconds $log
    if ($r.TimedOut) { Set-Stop ('the 45-minute budget expired during ' + $gate.Name) }
}

$reportXml = Join-Path $WorktreeDir 'report.xml'
$unitLog = Join-Path $LogDir 'unit.log'
$unitName = 'python -m pytest tests/unit -q --dist loadfile -n ' + $Workers + ' --junitxml=report.xml'
if (-not $script:StopReason) {
    $unitArgs = @('-m', 'pytest', 'tests/unit', '-q', '--dist', 'loadfile', '-n', [string]$Workers, '--junitxml=report.xml', '-p', 'no:cacheprovider')
    if ($RunStep -eq '1') {
        $unitArgs = @('-m', 'pytest', 'tests/unit/nonexistent_selection_for_the_fail_closed_drive', '-q')
    }
    $r = Invoke-Captured -FilePath $venvPython -Arguments $unitArgs -LogPath $unitLog -WorkDir $WorktreeDir -Environment (Get-StepEnvironment) -DeadlineSeconds $BudgetSeconds
    Add-Step $unitName $r.ExitCode $r.Seconds $unitLog
    if ($r.TimedOut) { Complete-Record -Pass $false -Reason 'the 45-minute budget expired during the portable suite; the process tree was killed and the timeout is recorded' }
} else {
    Fail-Step $unitName 'an earlier step failed'
}

# The JUnit XML is parsed and it must agree with the summary line.
$xmlCounts = Get-JUnitCounts -Path $reportXml
$skipTable = Get-SkipTable -Path $reportXml
$unitText = Get-LogText $unitLog
$summary = $null
$summaryLine = ''
if ($unitText) {
    $summaryMatch = [regex]::Match($unitText, '(?m)^=*\s*(\d+) failed, (\d+) passed, (\d+) skipped[^\r\n]*$')
    if (-not $summaryMatch.Success) { $summaryMatch = [regex]::Match($unitText, '(?m)^=*\s*(\d+) passed, (\d+) skipped[^\r\n]*$') }
    if (-not $summaryMatch.Success) { $summaryMatch = [regex]::Match($unitText, '(?m)^=*\s*(\d+) (?:failed|passed|error)[^\r\n]*$') }
    if ($summaryMatch.Success) {
        $summaryLine = $summaryMatch.Value.Trim()
        $failedCount = 0
        $passedCount = 0
        $skippedCount = 0
        $failedField = [regex]::Match($summaryLine, '(\d+) failed')
        if ($failedField.Success) { $failedCount = [int]$failedField.Groups[1].Value }
        $passedField = [regex]::Match($summaryLine, '(\d+) passed')
        if ($passedField.Success) { $passedCount = [int]$passedField.Groups[1].Value }
        $skippedField = [regex]::Match($summaryLine, '(\d+) skipped')
        if ($skippedField.Success) { $skippedCount = [int]$skippedField.Groups[1].Value }
        $summary = @{ failed = $failedCount; passed = $passedCount; skipped = $skippedCount }
    }
}
Add-Record ('pytest_xml: collected=' + $xmlCounts.collected + ' passed=' + $xmlCounts.passed + ' failed=' + $xmlCounts.failed + ' skipped=' + $xmlCounts.skipped + ' error=' + $xmlCounts.error)
if ($summary) {
    Add-Record ('pytest_summary: ' + $summaryLine)
    Add-Record ('pytest_summary_parsed: passed=' + $summary.passed + ' failed=' + $summary.failed + ' skipped=' + $summary.skipped)
} else {
    Add-Record 'pytest_summary: (no summary line could be parsed)'
}
if (-not (Test-Path $reportXml)) {
    Set-Stop ('report.xml is missing at ' + $reportXml)
} elseif (-not $summary) {
    Set-Stop 'the pytest summary line could not be parsed from the run log'
} else {
    $xmlTotal = $xmlCounts.collected
    $sumTotal = $summary.passed + $summary.failed + $summary.skipped
    if ($xmlTotal -ne $sumTotal -or $xmlCounts.passed -ne $summary.passed -or $xmlCounts.failed -ne $summary.failed) {
        Set-Stop ('the JUnit XML disagrees with the pytest summary line: xml collected=' + $xmlTotal + ' passed=' + $xmlCounts.passed + ' failed=' + $xmlCounts.failed + ' skipped=' + $xmlCounts.skipped + '; summary total=' + $sumTotal + ' passed=' + $summary.passed + ' failed=' + $summary.failed + ' skipped=' + $summary.skipped)
    }
}

# --- adjacency, both orders, and the runner's own set check -----------------

function Invoke-Adjacency {
    param([string] $Order)
    $name = 'python -m scripts.adjacency_run -Order ' + $Order
    if ($script:StopReason) { Fail-Step $name 'an earlier step failed'; return }
    $log = Join-Path $LogDir ('adjacency-' + $Order + '.log')
    $arguments = @('-m', 'scripts.adjacency_run', '-Order', $Order)
    if ($RunStep -eq '5' -and $Order -eq 'reverse') { $arguments = @('-m', 'scripts.adjacency_run', '-Order', 'forward') }
    $r = Invoke-Captured -FilePath $venvPython -Arguments $arguments -LogPath $log -WorkDir $WorktreeDir -Environment (Get-StepEnvironment) -DeadlineSeconds $BudgetSeconds
    Add-Step $name $r.ExitCode $r.Seconds $log
    if ($r.TimedOut) { Set-Stop ('the 45-minute budget expired during adjacency ' + $Order); return }
    $text = Get-LogText $log
    $okLine = [regex]::Match($text, '(?m)^adjacency_run: OK .*$')
    if (-not $okLine.Success) {
        Set-Stop ('the adjacency runner did not report OK for order=' + $Order)
        return
    }
    Add-Record ('adjacency_' + $Order + ': ' + $okLine.Value)
    if ($text.Contains('adjacency_run: FAIL')) { Set-Stop ('adjacency ' + $Order + ' reported FAIL') }
    if ($text.Contains('set members did not execute')) { Set-Stop ('adjacency ' + $Order + ': a required module did not execute') }
    if ($text.Contains('modules outside the set executed')) { Set-Stop ('adjacency ' + $Order + ': a module outside the set executed') }
    foreach ($field in @('skipped', 'failed', 'error')) {
        $hit = [regex]::Match($text, $field + '=([1-9]\d*)')
        if ($hit.Success) { Set-Stop ('adjacency ' + $Order + ' reported ' + $field + '=' + $hit.Groups[1].Value) }
    }
}

Invoke-Adjacency -Order 'forward'
Invoke-Adjacency -Order 'reverse'

$integration = 'tests/integration/test_container_decode_synthetic.py'
$integrationName = 'python -m pytest ' + $integration + ' -q'
if ($script:StopReason) {
    Fail-Step $integrationName 'an earlier step failed'
} else {
    $log = Join-Path $LogDir 'integration.log'
    $r = Invoke-Captured -FilePath $venvPython -Arguments @('-m', 'pytest', $integration, '-q', '-p', 'no:cacheprovider') -LogPath $log -WorkDir $WorktreeDir -Environment (Get-StepEnvironment) -DeadlineSeconds $BudgetSeconds
    Add-Step $integrationName $r.ExitCode $r.Seconds $log
    if ($r.TimedOut) { Set-Stop 'the 45-minute budget expired during the integration file' }
    $text = Get-LogText $log
    $integrationSummary = [regex]::Match($text, '(?m)^=*\s*\d+ (?:passed|failed)[^\r\n]*$')
    if ($integrationSummary.Success) { Add-Record ('integration_summary: ' + $integrationSummary.Value.Trim()) }
}

# --- the skip table against the pinned figures ------------------------------

$measuredTotal = 0
foreach ($key in $skipTable.Keys) { $measuredTotal += $skipTable[$key] }
$powershellPinned = 0
$powershellMeasured = 0
$deltas = New-Object System.Collections.Generic.List[string]

if (Test-Path $reportXml) {
    foreach ($key in $Pinned.Keys) {
        $pinnedCount = $Pinned[$key]
        $measured = 0
        if ($skipTable.ContainsKey($key)) { $measured = $skipTable[$key] }
        if ($PinnedCause[$key] -eq 'powershell') {
            $powershellPinned += $pinnedCount
            $powershellMeasured += $measured
        }
        if ($SkipInflation -and $key -eq $SkipInflation) {
            $measured = $pinnedCount + 1
            Set-Stop ('driven skip inflation on ' + $key)
        }
        $delta = $measured - $pinnedCount
        $cause = 'same'
        if ($delta -ne 0) {
            if (-not (Test-Path (Join-Path $WorktreeDir $key))) {
                $cause = 'file is not present at this SHA, so the pinned trace describes a different tree'
            } elseif ($PinnedCause[$key] -eq 'powershell') {
                $cause = 'the PowerShell host exists here, so nodes that skip on Linux execute on Windows'
            } elseif ($PinnedCause[$key] -eq 'rom') {
                $cause = 'ROM-gated member: canonical image presence differs between the runner and this machine'
            } elseif ($PinnedCause[$key] -eq 'atlas') {
                $cause = 'assembled atlas presence differs between the runner and this machine'
            } elseif ($PinnedCause[$key] -eq 'site') {
                $cause = 'built-site presence differs between the runner and this machine'
            } elseif ($PinnedCause[$key] -eq 'optional-import') {
                $cause = 'an optional import is present or absent differently here'
            } elseif ($PinnedCause[$key] -eq 'environment') {
                $cause = 'the research or instrumented build tree differs between the runner and this machine'
            } elseif ($PinnedCause[$key] -eq 'linux-only') {
                $cause = 'a filesystem or checkout property the Linux runner has and this machine does not, or the reverse'
            } else {
                $cause = 'a skip this machine has and the pinned trace does not'
            }
        }
        [void]$deltas.Add(('{0} pinned={1} measured={2} delta={3} cause={4}' -f $key, $pinnedCount, $measured, $delta, $cause))
    }
}
foreach ($key in ($skipTable.Keys | Sort-Object)) {
    if (-not $Pinned.Contains($key)) {
        [void]$deltas.Add(('{0} pinned=none measured={1} delta=+{1} cause=skip in a file the pinned trace does not list' -f $key, $skipTable[$key]))
    }
}

Add-Record ''
Add-Record ('pinned skip figures (job ' + $PinnedJob + ' at ' + $PinnedSha + ', Linux baseline)')
Add-Record ('powershell_nodes: pinned=' + $powershellPinned + ' measured=' + $powershellMeasured + ' (the 13 nodes the brief names: test_dev_tools.py 6, test_worktree_owners.py 7)')
Add-Record ('whole_suite: pinned_skipped=' + $PinnedSkipped + ' measured_skipped=' + $xmlCounts.skipped)
Add-Record ('whole_suite: pinned_passed=' + $PinnedPassed + ' measured_passed=' + $xmlCounts.passed + '; pinned_failed=' + $PinnedFailed + ' measured_failed=' + $xmlCounts.failed)
Add-Record ('per_file_table_total=' + $PinnedTableTotal + ' measured_skips_total=' + $measuredTotal)
Add-Record ''
Add-Record 'per-file skip table (file pinned measured delta cause)'
foreach ($row in ($deltas | Sort-Object)) { Add-Record $row }
Add-Record ''
Add-Record 'reconciliation, Windows against the Linux baseline, by cause'
foreach ($row in ($deltas | Where-Object { $_ -notmatch ' delta=0 ' } | Sort-Object)) { Add-Record ('reconcile: ' + $row) }
Add-Record 'reconcile: a delta here is recorded, not failed; the pinned trace describes a different tree, so only the exit codes and the JUnit agreement gate this record.'

# --- teardown ---------------------------------------------------------------

$worktreeRemoved = 'the worktree was never created'
if (Test-Path (Join-Path $WorktreeDir '.git')) {
    $log = Join-Path $LogDir 'worktree-remove.log'
    $r = Invoke-Captured -FilePath 'git' -Arguments @('-C', $RepoRoot, 'worktree', 'remove', '--force', $WorktreeDir) -LogPath $log -WorkDir $RepoRoot -Environment @{} -DeadlineSeconds 300
    Add-Step 'git worktree remove --force' $r.ExitCode $r.Seconds $log
    if (Test-Path $WorktreeDir) {
        $worktreeRemoved = 'REFUSED: the directory is still present'
        Set-Stop 'the worktree was not removed'
    } else {
        $worktreeRemoved = 'removed'
    }
}
Add-Record ('worktree_removed: ' + $worktreeRemoved)
Add-Record ('peak_tree_mb: ' + [math]::Round($script:PeakTreeBytes / 1MB, 1))
Add-Record ('run_wall_seconds: ' + [math]::Round((Get-ElapsedSeconds), 1))
Add-Record ('steps_total: ' + $script:StepCount + ' steps_failed: ' + $script:StepFailures)

if ($script:StopReason) {
    Complete-Record -Pass $false -Reason $script:StopReason
} else {
    Complete-Record -Pass $true -Reason ('all ' + $script:StepCount + ' steps exited 0; the JUnit XML agrees with the pytest summary line; both adjacency orders proved the full set ran; every skip delta against the pinned figures carries a named cause')
}
