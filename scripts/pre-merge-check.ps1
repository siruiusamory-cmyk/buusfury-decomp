# Pre-merge check: is the reviewed candidate still valid against live master?
#
# MEASURED SAMPLE (2026-10-12, this session's own merges). Read-only `glab api`
# on MRs 230, 234 and 235, plus git ancestry in this repository, gave:
#
#   MR   recorded base_sha   master tip at merge   commits master gained
#                                                 between fork and merge
#   230  1016ab49             c3fc145c              10
#   234  f097898b             f097898b               0
#   235  a8a2da5d             a8a2da5d               0
#
# So one of three merges had drifted at merge time (MR 230, ten commits), and
# the other two merged against exactly the master they were cut from.
#
# TRUTHFUL RESULT ON THAT ONE, because it is the whole justification for this
# gate's false-positive rate: from fork 1016ab49, BOTH sides changed
# `docs/research/PROJECT_STATE_AUDIT_RECONCILIATION.md`, so this script exits 1
# and names that file. That merge composed cleanly (merge-tree reproduces the
# recorded tree e3466f9a) and its post-merge master pipeline (2938640540) was
# green. So on the measured sample the gate stops 1 of 1 drifted merges, and that
# one was a documentation path with no textual conflict.
#
# WHAT THIS TRADES. A both-sides path costs a rebase onto live master and a
# re-run of the focused tests: minutes, and the gate's own failure text asks for
# exactly that. What it buys is the class of interaction no pipeline checks
# before the merge, where two lanes edit one file with no textual conflict and
# the composition is never tested. That shape is the MAP-PAINT-class regression.
# The trade is kept on the review of RETRO-CI-002-20261012-112919.
#
# The combination is only at risk where master changed a path this candidate
# also changed, so that is what this script measures, and it is the whole gate.
#
# `git merge-tree --write-tree <target> <candidate>` was verified as the same
# computation GitLab performs for a regular merge commit (no squash): replayed on
# all three merges above, against each merge commit's own first parent, it
# reproduces the recorded merge commit's tree exactly (MR 230 e3466f9a..., MR 234
# 7aa451d9..., MR 235 d4363cab...). It is printed as the predicted merged tree
# and never checked unless the caller supplies a digest with `-ExpectMergedTree`;
# no such digest is recorded anywhere today, so in practice the tree is printed and
# not checked, and a mismatch with a supplied digest is the only check on it. That
# is deliberate: the tree changes whenever the target moves even when nothing
# interacts, and failing on that alone would be a gate nobody uses.
#
# Contract:
#   - fail closed when the target changed a path the candidate changed, or when
#     the merge conflicts;
#   - never in the primary checkout, and never anywhere but the root of a
#     worktree. A path with no `.git` at its root is refused by the test above
#     the compare, and its message names the checkout root git reports for that
#     path, so a subdirectory of the primary is refused too. The primary itself
#     is refused structurally by the compare below: at a worktree root it answers
#     `.git` for `git rev-parse --git-dir`, and a bare `.` is refused as well, so
#     no machine-specific path is written down here. A linked worktree of the
#     primary answers an absolute `--git-dir` and IS allowed: every ticket
#     worktree is one, so this gate runs in a linked worktree or not at all;
#   - push nothing, merge nothing. It does WRITE: `git fetch` creates
#     remote-tracking refs under the shared `.git`, and `merge-tree --write-tree`
#     writes tree and blob objects, in a linked worktree into the primary's
#     `--git-common-dir`. Nothing else is touched: no branch, no index, no
#     working tree, no remote.
#
# PROPOSED gate semantics, awaiting the coordinator's ruling: a candidate that
# changes a file listed in config/rom-dependent-tests.txt stops as FOCUSED ROM RUN
# REQUIRED, because those nodes SKIP on a GitHub runner; scripts/rom-focused-check.ps1
# is the run that covers them, against a private copy of the canonical image.

[CmdletBinding()]
param(
    # The reviewed candidate, by commit or ref.
    [Parameter(Mandatory = $true)]
    [string]$Ref,

    # The branch the candidate is to be merged into, on the remote.
    [string]$TargetBranch = 'master',

    # The remote the target is read from.
    [string]$Remote = 'origin',

    # The checkout to measure in. Must be a git worktree; the primary checkout is
    # refused structurally.
    [string]$RepoPath = (Get-Location).Path,

    # Skip the fetch of the target when the caller has already fetched it.
    [switch]$NoFetch,

    # The merged tree digest a caller can supply. No such digest is recorded
    # anywhere today, so this is absent by default and the predicted tree is then
    # only printed. When it is supplied, a mismatch with the freshly predicted tree
    # is a failure.
    [string]$ExpectMergedTree,

    # Report an overlap without failing. Never a silent default: the caller asks
    # for it by name.
    [switch]$ReportOnly
)

$ErrorActionPreference = 'Stop'

function Invoke-Git {
    # `Label` names the step for the failure message. The label is used rather
    # than a re-run of the arguments because no argument here may carry braces:
    # Windows PowerShell consumes `{` and `}` on the way to a native command, so
    # a revision expression written with `^{commit}` would reach git as
    # `HEAD^commit` and fail as an unknown revision.
    param([string]$Label, [string[]]$Arguments)
    $output = & git -C $RepoPath @Arguments 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw ("git $Label failed ($LASTEXITCODE) in ${RepoPath}: " + ($output -join ' '))
    }
    return @($output)
}

function Get-ChangedPaths {
    param([string]$Spec)
    $lines = & git -C $RepoPath diff --name-only $Spec 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "git diff --name-only $Spec failed ($LASTEXITCODE)"
    }
    return @($lines | Where-Object { $_ } | ForEach-Object { $_.ToString() })
}

# --- which checkout is this ---------------------------------------------------
# Structural, never a name: the primary checkout answers `.git` for
# `--git-dir`, and a linked worktree answers `<common>/worktrees/<name>`, which
# is an absolute path. That comparison needs no absolute-path translation, which
# matters because `--path-format=absolute` still hands back an MSYS2 form here
# (`/home/<user>/...`) rather than a drive-letter path.
if (-not (Test-Path -LiteralPath (Join-Path $RepoPath '.git'))) {
    # Not the root of a worktree: git names the checkout the path sits in, and
    # that checkout - the primary, for a subdirectory of it - is what is refused.
    # The pipe stays INSIDE the @(): the same pipeline outside it collapses a
    # single line to a scalar string, and `[0]` then indexes a character.
    $root = @(& git -C $RepoPath rev-parse --show-toplevel 2>$null | Where-Object { $_ })
    if ($root.Count -eq 0) {
        throw "${RepoPath} is not a git worktree (no .git at its root, and git reports no checkout)"
    }
    throw ("${RepoPath} is not the root of a git worktree; it sits in the checkout " +
        "$($root[0].ToString().Trim()). It refuses the primary checkout and any path inside it: " +
        'run the gate from the root of a ticket worktree')
}
& git -C $RepoPath rev-parse --is-inside-work-tree 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "$RepoPath is not a git worktree"
}
$gitDir = @(& git -C $RepoPath rev-parse --git-dir 2>$null | Where-Object { $_ })
if ($gitDir.Count -ne 1) {
    throw "git rev-parse --git-dir answered $($gitDir.Count) lines in ${RepoPath}"
}
$gitDir = $gitDir[0].ToString().Trim()
# Stated limit: a $GIT_DIR in the environment makes --git-dir absolute in the primary, which slips past this compare.
if ($gitDir -eq '.git' -or $gitDir -eq '.') {
    throw ("refusing to run in the primary checkout ${RepoPath}: its git directory is the " +
        'repository itself (git answers `.` or `.git` there), so it is the main worktree. Use a ' +
        'ticket worktree; a linked worktree answers an absolute --git-dir under the common ' +
        'directory')
}

# --- the ROM-dependent inventory, read before anything else can go wrong ------
# Fail closed. A gate that cannot tell whether this candidate needs the focused
# run must never report that a green GitHub run covers it.
$inventoryPath = Join-Path $RepoPath 'config/rom-dependent-tests.txt'
if (-not (Test-Path -LiteralPath $inventoryPath -PathType Leaf)) {
    throw ("config/rom-dependent-tests.txt is missing from ${RepoPath}: without it this gate cannot " +
        'tell a candidate a green GitHub run covers from one whose tests SKIP there, so it refuses ' +
        'instead of assuming the run covers it')
}
$romInventory = @(Get-Content -LiteralPath $inventoryPath |
    ForEach-Object { $_.Trim() } |
    Where-Object { $_ -and -not $_.StartsWith('#') } |
    ForEach-Object { $_.Replace('\', '/').ToLowerInvariant() })
if ($romInventory.Count -eq 0) {
    throw ("config/rom-dependent-tests.txt in ${RepoPath} lists no test file: an empty inventory " +
        'would classify every candidate as covered by a GitHub run, so it is refused instead')
}

# --- how git resolved each end, without braces in any argument ----------------
function Resolve-Revision {
    param([string]$Revision, [string]$What)
    $resolved = & git -C $RepoPath rev-parse --verify --quiet "$Revision~0" 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $resolved) {
        throw "unknown ${What}: $Revision"
    }
    return (@($resolved) -join '').Trim()
}

# --- read the two ends --------------------------------------------------------
if (-not $NoFetch) {
    # A fetch only. It writes remote-tracking refs under the shared `.git` and
    # touches no branch, no index and no working tree, so it cannot change what
    # is under review.
    Invoke-Git -Label "fetch $Remote $TargetBranch" -Arguments @('fetch', '--quiet', $Remote, $TargetBranch) | Out-Null
}

$targetRef = "refs/remotes/$Remote/$TargetBranch"
$targetTip = Resolve-Revision -Revision $targetRef -What "$Remote/$TargetBranch"
$candidate = Resolve-Revision -Revision $Ref -What 'candidate'

Write-Output "pre-merge-check: candidate $candidate"
Write-Output "pre-merge-check: $Remote/$TargetBranch $targetTip"

# --- has the target moved, and does it touch anything this candidate touched? --
& git -C $RepoPath merge-base --is-ancestor $targetTip $candidate 2>$null
$targetIsAncestor = $LASTEXITCODE -eq 0

$fork = (Invoke-Git -Label 'merge-base' -Arguments @('merge-base', $candidate, $targetTip) | Select-Object -First 1).ToString().Trim()
$mine = Get-ChangedPaths "$fork..$candidate"
$theirs = Get-ChangedPaths "$fork..$targetTip"
$overlap = @($mine | Where-Object { $theirs -contains $_ } | Sort-Object)

Write-Output ("pre-merge-check: fork $fork; candidate changed {0} paths; " -f $mine.Count)
Write-Output ("pre-merge-check: $Remote/$TargetBranch changed {0} paths since that fork; {1} in both" `
        -f $theirs.Count, $overlap.Count)

# --- the record requirement: is a GitHub run enough for this candidate? -------
# Driven from `$mine`, the paths the candidate already changed. Path-based by
# design: it is the file that needs the image, not the shape of the edit.
$romTouching = @($mine |
    Where-Object { $romInventory -contains $_.Replace('\', '/').ToLowerInvariant() } |
    Sort-Object)

# --- the predicted merged tree (the merge commit's own computation) -----------
$mergeOutput = & git -C $RepoPath merge-tree --write-tree $targetTip $candidate 2>$null
$mergeTreeFailed = $LASTEXITCODE -ne 0
$predictedTree = (@($mergeOutput) | Select-Object -First 1).ToString().Trim()
Write-Output "pre-merge-check: predicted merged tree $predictedTree"

$failures = @()
$instructions = @()
if ($mergeTreeFailed) {
    $failures += 'git merge-tree could not produce a tree: the merge conflicts'
    $instructions += 'resolve the conflict against the current target tip'
}
if ($overlap.Count -gt 0) {
    $failures += "$($overlap.Count) path(s) changed on both sides: $($overlap -join ', ')"
    $instructions += ("rebase onto live $Remote/$TargetBranch, re-run the focused tests for the " +
        'paths above, and re-request the review')
}
if (-not $targetIsAncestor -and $overlap.Count -eq 0 -and -not $mergeTreeFailed) {
    Write-Output ("pre-merge-check: $Remote/$TargetBranch moved under the candidate, but no path it " +
        'changed since the fork is a path this candidate changed, so the two sides compose ' +
        'without an interaction')
}
if ($ExpectMergedTree) {
    $expected = $ExpectMergedTree.Trim().ToLower()
    if ($predictedTree -ne $expected) {
        $failures += "predicted merged tree $predictedTree is not the reviewed $expected"
        $instructions += 'rebase onto live master and re-run the focused tests, then re-request'
    }
}
if ($romTouching.Count -gt 0) {
    $instructions += ('run the ROM-dependent tests named by config/rom-dependent-tests.txt against a ' +
        'PRIVATE COPY of the canonical image, with the canonical SHA-256 checked before and after, by ' +
        'powershell -NoProfile -ExecutionPolicy Bypass -File scripts\rom-focused-check.ps1; a full ' +
        'local record is not required')
}

$romRequired = $romTouching.Count -gt 0
if (-not $romRequired) {
    Write-Output ('pre-merge-check: record requirement: GITHUB RUN SUFFICES ' +
        '(no changed path is a ROM-dependent test file)')
}
else {
    Write-Output (("pre-merge-check: record requirement: FOCUSED ROM RUN REQUIRED ({0} changed path(s) " +
        'need the canonical image and SKIP on GitHub: {1})') `
        -f $romTouching.Count, ($romTouching -join ', '))
}

if ($failures.Count -eq 0 -and -not $romRequired) {
    Write-Output 'pre-merge-check: PASS'
    exit 0
}

# One line per condition, so a reader never has to infer which verdict fired, and
# the rebase text is never printed for a candidate whose only stop is the ROM one.
if ($romRequired) {
    Write-Output 'pre-merge-check: FOCUSED ROM RUN REQUIRED'
}
if ($failures.Count -gt 0) {
    Write-Output 'pre-merge-check: REBASE REQUIRED'
    foreach ($failure in $failures) {
        Write-Output "  - $failure"
    }
}
if ($ReportOnly) {
    Write-Output 'pre-merge-check: -ReportOnly, so this is a report and not a stop'
    exit 0
}
Write-Output 'pre-merge-check: next step, in this order:'
$step = 0
foreach ($instruction in $instructions) {
    $step++
    Write-Output "  $step. $instruction"
}
if ($failures.Count -gt 0) {
    Write-Output ("pre-merge-check: the target moved onto work this candidate's pipeline never tested " +
        'together with it; the rebase plus the focused tests is minutes, and the alternative is a ' +
        'silent interaction discovered after the merge')
}
if ($romRequired) {
    Write-Output ('pre-merge-check: a GitHub run cannot cover the paths above, because those nodes ' +
        'SKIP without the canonical image; the focused run against a private copy is what covers them')
}
exit 1
