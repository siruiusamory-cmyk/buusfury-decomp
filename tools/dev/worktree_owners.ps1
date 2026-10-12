# One implementation of the one-writer sweep: which sibling worktree holds which
# file, and whether that dirt is the writer's or master's own blob arriving
# mid-merge (dbz-dev retro 1.1: a mid-merge carrier was read as a live writer and
# nearly blocked a ticket). scripts\new-ticket-worktree.ps1 calls the function; a
# lane that is already in a worktree runs the file, which sweeps and exits.
#
#   powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\dev\worktree_owners.ps1
#   powershell.exe ... -File tools\dev\worktree_owners.ps1 -SweepOnly -Markdown
#
# -SweepOnly prints the sweep and exits 0; the switch exists so a caller reads
#   the same thing the cutter prints, without any behaviour depending on it.
# -Markdown appends one table row per held file, for a check-in comment.
# -Json prints one machine-readable object; a guard test reads this rather than
#   parsing prose.
# -Path/-Baseline/-MaxFiles exist for a test that builds its own repository.
#
# Read-only: it runs `git worktree list`, `git status`, `git hash-object` and
# `git cat-file`. It writes no file, no index entry and no ref.

[CmdletBinding()]
param(
    # -Repository and -Baseline exist so a guard can point the sweep at a
    # repository it built; the defaults sweep the checkout this file lives in.
    [string]$Repository,
    [string]$Baseline,
    [switch]$SweepOnly,
    [switch]$Markdown,
    [switch]$Json,
    [int]$MaxFiles = 8
)

$ErrorActionPreference = 'Stop'

function Invoke-GitCommand {
    # PowerShell 5.1 turns a native command's stderr into a terminating
    # NativeCommandError whenever the caller redirects a stream, so every git
    # call runs with the preference relaxed and is judged by its exit code.
    param([Parameter(Mandatory)][string[]]$Arguments, [string]$Repository)

    $ErrorActionPreference = 'Continue'
    try {
        $output = & git -C $Repository @Arguments 2>&1
        $exit = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = 'Stop'
    }
    return [pscustomobject]@{ Output = @($output); Exit = $exit }
}

function Get-WorktreeEntryClass {
    <#
    One dirty file's classification. The staged content is compared against the
    repository's own blob at the baseline: unequal means this worktree is the
    only place that version exists, so the lane is holding an edit the caller
    must not touch.
    #>
    param(
        [Parameter(Mandatory)][string]$WorktreePath,
        [Parameter(Mandatory)][string]$Entry,
        [Parameter(Mandatory)][string]$Repository,
        [Parameter(Mandatory)][string]$BaseRef,
        [string]$BaseSha
    )

    if ($Entry -match '^(DD|AU|UD|UA|DU|AA|UU) ') { return 'conflicted' }
    $relative = ($Entry -replace '^.. ', '').Trim()
    if ($relative -match ' -> ') { $relative = ($relative -split ' -> ')[-1].Trim('"') }
    $absolute = Join-Path $WorktreePath $relative
    $staged = $Entry[0] -ne '?' -and $Entry[0] -ne ' '
    # git reports an untracked directory with a trailing slash and no mtime of its
    # own; it is new to the branch by definition, and treating it as a missing file
    # printed it as [deleted] in the first measurement of this sweep.
    if ($relative.EndsWith('/') -or (Test-Path -LiteralPath $absolute -PathType Container)) {
        return 'new-in-branch'
    }
    $present = Test-Path -LiteralPath $absolute -PathType Leaf

    if (-not $present) {
        if (-not $staged) { return 'deleted' }
        # A staged delete has no file to hash: the blob comparison is still the
        # question, so hash the content the index holds rather than the file.
        $stagedContent = Invoke-GitCommand -Repository $WorktreePath -Arguments @('show', (':' + $relative))
        if ($stagedContent.Exit -ne 0) { return 'unreadable' }
        # Piped through hash-object with `--path`, so the smudge/clean filters the
        # index applies are applied here too.
        $thisHash = ($stagedContent.Output | & git -C $WorktreePath hash-object --stdin --path $relative 2>&1 | Out-String).Trim()
        if ($LASTEXITCODE -ne 0) { return 'unreadable' }
    } else {
        # `hash-object <path>` applies the same conversion `git add` would, which
        # `--stdin` does not: on a CRLF checkout `--stdin` hashed 14 bytes where
        # the blob is 13, and every file looked authored.
        $thisHash = (& git -C $WorktreePath hash-object -- $relative 2>&1 | Out-String).Trim()
        if ($LASTEXITCODE -ne 0) { return 'unreadable' }
    }

    $inBranch = (Invoke-GitCommand -Repository $WorktreePath -Arguments @('cat-file', '-e', ($BaseRef + ':' + $relative))).Exit -eq 0
    if (-not $inBranch) { return 'new-in-branch' }

    $reference = if ($BaseSha) { $BaseSha } else { $BaseRef }
    $baseHash = (& git -C $WorktreePath rev-parse ($reference + ':' + $relative) 2>&1 | Out-String).Trim()
    if ($LASTEXITCODE -ne 0) { return 'unreadable' }
    if ($baseHash -eq $thisHash) { return 'carries-master' }
    return 'authored'
}

function Invoke-WorktreeOwnershipSweep {
    <#
    Head line, one line per registered worktree, then one line per dirty file
    carrying its mtime, its staged-or-worktree origin and its classification.
    #>
    param(
        [string]$Repository,
        [string]$Baseline,
        [switch]$Markdown,
        [switch]$Json,
        [int]$MaxFiles = 8
    )

    if (-not $Repository) { $Repository = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path }
    # An explicitly passed empty string is BOUND, so a declared default never
    # applies to it; both are resolved in the body for that reason.
    if (-not $Baseline) { $Baseline = 'origin/master' }
    $Repository = (Resolve-Path -LiteralPath $Repository).Path

    $baseSha = $null
    $base = Invoke-GitCommand -Repository $Repository -Arguments @('rev-parse', '--verify', '--quiet', $Baseline)
    if ($base.Exit -eq 0) { $baseSha = ($base.Output -join "`n").Trim() }

    $list = Invoke-GitCommand -Repository $Repository -Arguments @('worktree', 'list', '--porcelain')
    $paths = [System.Collections.Generic.List[string]]::new()
    $branches = @{}
    $current = $null
    foreach ($line in $list.Output) {
        if ($line.StartsWith('worktree ')) {
            # `git worktree list` prints some entries as an MSYS path (/c/Dev/...)
            # on this machine. Git accepts either, but Join-Path and the printed
            # table only read the Windows spelling.
            $current = $line.Substring(9)
            if ($current -match '^/([A-Za-z])/(.*)$') {
                $current = ($Matches[1].ToUpperInvariant() + ':\' + ($Matches[2] -replace '/', '\'))
            }
            $paths.Add($current)
            $branches[$current] = '(detached HEAD)'
        } elseif ($line.StartsWith('branch ') -and $current) {
            $branches[$current] = $line.Substring(7) -replace '^refs/heads/', ''
        }
    }

    $rows = [System.Collections.Generic.List[object]]::new()
    foreach ($worktree in $paths) {
        $status = Invoke-GitCommand -Repository $worktree -Arguments @('status', '--porcelain')
        if ($status.Exit -ne 0) {
            # A stale entry (moved or deleted worktree) must say so rather than
            # report the zero files git printed nothing about.
            $rows.Add([pscustomobject]@{
                worktree = $worktree; branch = $branches[$worktree]; unreadable = $true
                files = @(); more = 0
            })
            continue
        }
        $entries = @($status.Output)
        $files = [System.Collections.Generic.List[object]]::new()
        foreach ($entry in ($entries | Select-Object -First $MaxFiles)) {
            $relative = ($entry -replace '^.. ', '').Trim()
            $absolute = Join-Path $worktree $relative
            $files.Add([pscustomobject]@{
                entry    = $entry
                mtime    = if (Test-Path -LiteralPath $absolute -PathType Leaf) {
                               [System.IO.File]::GetLastWriteTime($absolute).ToString('yyyy-MM-dd HH:mm:ss')
                           } else { '-' }
                origin   = if ($entry[0] -eq '?') { 'untracked' } elseif ($entry[0] -eq ' ') { 'worktree' } else { 'staged' }
                clas     = Get-WorktreeEntryClass -WorktreePath $worktree -Entry $entry `
                             -Repository $Repository -BaseRef $Baseline -BaseSha $baseSha
            })
        }
        $rows.Add([pscustomobject]@{
            worktree = $worktree; branch = $branches[$worktree]; unreadable = $false
            files = @($files); more = [Math]::Max(0, $entries.Count - $MaxFiles)
        })
    }

    if ($Json) {
        [pscustomobject]@{
            baseline = $Baseline
            baseline_sha = $baseSha
            worktrees = @($rows)
        } | ConvertTo-Json -Depth 6
        return
    }

    Write-Host ('ownership sweep: sibling worktrees, branch, uncommitted files (baseline {0})' -f $Baseline)
    if ($Markdown) { Write-Host '| worktree | branch | file | mtime | origin | class |'; Write-Host '|---|---|---|---|---|---|' }
    foreach ($row in $rows) {
        if ($row.unreadable) {
            Write-Host ("  {0}  [{1}]  unreadable: git status exited non-zero" -f $row.worktree, $row.branch)
            continue
        }
        if ($row.files.Count -eq 0) { continue }
        Write-Host ("  {0}  [{1}]  {2} uncommitted file(s)" -f $row.worktree, $row.branch, ($row.files.Count + $row.more))
        foreach ($file in $row.files) {
            if ($Markdown) {
                Write-Host ('| {0} | {1} | {2} | {3} | {4} | {5} |' -f
                    $row.worktree, $row.branch, $row.file, $file.mtime, $file.origin, $file.clas)
            } else {
                Write-Host ("    [{0}] {1}  {2}  {3}" -f $file.clas, $file.entry, $file.mtime, $file.origin)
            }
        }
        if ($row.more -gt 0) { Write-Host ("    ... and {0} more" -f $row.more) }
    }
}

# Set by name: interpolating $MyInvocation.InvocationName directly prints the
# member's own type name under this shell, while the variable holds '.' or the path.
$invocationName = $MyInvocation.InvocationName
if ($invocationName -ne '.') {
    Invoke-WorktreeOwnershipSweep -Repository $Repository -Baseline $Baseline -Markdown:$Markdown -Json:$Json -MaxFiles $MaxFiles
    exit 0
}
