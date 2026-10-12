# Cut a ticket worktree that is ready to work in: a frozen base SHA read from
# live origin/master, the shared test venv junctioned in as `.venv`, and an
# ownership sweep of every sibling worktree so a writer can see what is held.
param(
    [string]$Ticket,
    [string]$Branch,
    [string]$Parent,
    [switch]$SiteGates
)

$ErrorActionPreference = 'Stop'

if (-not $Ticket -or -not $Branch) {
    Write-Host 'usage: scripts\new-ticket-worktree.ps1 -Ticket <id> -Branch <name> [-Parent <dir>] [-SiteGates]'
    Write-Host '  -Ticket    ticket id, for example RETRO-ENV-001'
    Write-Host '  -Branch    branch to create, for example ticket/retro-env-001'
    Write-Host '  -Parent    directory to hold the worktree (default: alongside this checkout)'
    Write-Host '  -SiteGates also run `npm ci` in the new worktree, about four minutes, because the'
    Write-Host '             site commands (`npm run check`, `npm run build`) read node_modules;'
    Write-Host '             the Python gates do not need it'
    exit 2
}

$RepoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
if (-not $Parent) { $Parent = Split-Path -Parent $RepoRoot }
$Worktree = Join-Path $Parent ('log1-remake-' + $Ticket.ToLowerInvariant())

# The shared test venv is the sibling worktree named below, searched for upward
# from this checkout rather than written as one machine's path, the same lookup
# scripts\test.ps1 uses.
$SharedSibling = 'log1-remake-test-speed-003\build\test-speed-003\venv'
$SharedVenv = $null
$search = $RepoRoot
while ($search) {
    $probe = Join-Path $search $SharedSibling
    if (Test-Path -LiteralPath (Join-Path $probe 'Scripts\python.exe') -PathType Leaf) { $SharedVenv = $probe; break }
    $up = Split-Path $search -Parent
    if (-not $up -or $up -eq $search) { break }
    $search = $up
}

if (Test-Path -LiteralPath $Worktree) { throw "Already exists: $Worktree" }
if (-not $SharedVenv) { throw "Shared test venv not found: no $SharedSibling above $RepoRoot" }

# PowerShell 5.1 turns a native command's stderr into a terminating
# NativeCommandError whenever the caller redirects a stream (measured 2026-10-12:
# `git worktree add` progress text under `*>`, and a stale worktree entry under
# `git status`), so every git call runs with the preference relaxed and is judged
# by its exit code, with git's own words printed when it fails.
function Invoke-Git {
    param([Parameter(Mandatory)][string[]]$Arguments, [string]$Path = $RepoRoot)

    $ErrorActionPreference = 'Continue'
    try {
        $output = & git -C $Path @Arguments 2>&1
        $exit = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = 'Stop'
    }
    if ($exit -ne 0) {
        Write-Host "git $($Arguments -join ' ') exited $exit"
        $output | ForEach-Object { Write-Host "  $_" }
    }
    return [pscustomobject]@{ Output = @($output); Exit = $exit }
}

$git = Invoke-Git 'fetch', 'origin', '--prune'
if ($git.Exit -ne 0) { exit $git.Exit }

# The frozen base is the fetched tip, resolved once and passed to the add, so the
# worktree cannot start from a branch that moved between the two commands.
$git = Invoke-Git 'rev-parse', 'origin/master'
if ($git.Exit -ne 0) { exit $git.Exit }
$Base = ($git.Output -join "`n").Trim()
Write-Host "base:     $Base (frozen: live origin/master, fetched just now)"

$git = Invoke-Git 'worktree', 'add', '-b', $Branch, $Worktree, $Base
if ($git.Exit -ne 0) { exit $git.Exit }

New-Item -ItemType Junction -Path (Join-Path $Worktree '.venv') -Target $SharedVenv | Out-Null
Write-Host "venv:     junction -> $SharedVenv"

if ($SiteGates) {
    Write-Host 'site gates: npm ci (about four minutes)'
    Push-Location $Worktree
    & npm ci
    $npmExit = $LASTEXITCODE
    Pop-Location
    if ($npmExit -ne 0) { exit $npmExit }
}

# Ownership sweep: one writer per file. Every sibling worktree is listed with its
# branch and its uncommitted file count, and up to eight of those paths, which is
# what a new lane needs to see before it claims a surface.
Write-Host 'ownership sweep: sibling worktrees, branch, uncommitted files'
$list = Invoke-Git 'worktree', 'list', '--porcelain'
$paths = [System.Collections.Generic.List[string]]::new()
$branches = @{}
$current = $null
foreach ($line in $list.Output) {
    if ($line.StartsWith('worktree ')) {
        $current = $line.Substring(9)
        $paths.Add($current)
        $branches[$current] = '(detached HEAD)'
    } elseif ($line.StartsWith('branch ') -and $current) {
        $branches[$current] = $line.Substring(7) -replace '^refs/heads/', ''
    }
}
foreach ($path in $paths) {
    $status = Invoke-Git -Path $path -Arguments 'status', '--porcelain'
    if ($status.Exit -ne 0) {
        # A stale entry (moved or deleted worktree) must say so rather than
        # report the zero files git printed nothing about.
        Write-Host ("  {0}  [{1}]  unreadable: git status exited {2}" -f $path, $branches[$path], $status.Exit)
        continue
    }
    Write-Host ("  {0}  [{1}]  {2} uncommitted file(s)" -f $path, $branches[$path], $status.Output.Count)
    foreach ($entry in $status.Output | Select-Object -First 8) { Write-Host "    $entry" }
    if ($status.Output.Count -gt 8) { Write-Host ("    ... and {0} more" -f ($status.Output.Count - 8)) }
}
