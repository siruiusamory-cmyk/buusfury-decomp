# Copy named files into a DETACHED worktree at a named commit, hash-verify every
# copy against its source, and refuse to continue when a byte differs. Its whole
# point is provenance for a discrimination probe: the measured failure (dbz-dev
# retro 1.6) was a `cmd /c "... > file"` redirect that converted line endings, so a
# probe ran the new journal against the new tests and passed; only a blob mismatch
# (`ffe03a38...` against the commit's `7ef89678...`) exposed it.
#
#   powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\dev\probe_worktree.ps1 `
#       -Path tools\webfoot\journal.py -Sha <commit>
#
# The worktree lives under build/ (ignored) and is removed when the check ends,
# unless -Keep asks for it. Nothing is committed, staged or pushed, and the
# caller's own worktree is never modified.
#
# Exit 0 only when every named file was copied and every copy matched. A mismatch
# prints both digests and exits 3 with the copy still on disk for inspection.

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string[]]$Path,
    [string]$Sha = 'HEAD',
    [string]$Repository,
    # An existing worktree to verify INSTEAD of copying: the refusal path, and the
    # way to re-audit a probe that has already been built.
    [string]$VerifyOnly,
    [switch]$Keep,
    [switch]$CheckOnly
)

$ErrorActionPreference = 'Stop'
# The repository under probe is the INVOKING tree, not the tree this script lives
# in: a lane runs the tool from the worktree it is probing.
if (-not $Repository) { $Repository = (Get-Location).Path }
$root = (Resolve-Path -LiteralPath $Repository).Path

function Invoke-GitCommand {
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

# The named commit must resolve to a full SHA first: a probe whose provenance is
# "HEAD" is not provenance, because the caller's HEAD can move under the run.
$resolved = Invoke-GitCommand -Repository $root -Arguments @('rev-parse', '--verify', '--quiet', $Sha)
if ($resolved.Exit -ne 0) {
    Write-Host "probe worktree: cannot resolve '$Sha' to a commit"
    exit 2
}
$commit = ($resolved.Output -join "`n").Trim()
Write-Host "probe worktree: commit $commit"

# The paths must exist in the caller's tree before a worktree is created, and the
# source bytes are hashed BEFORE the copy so a mismatch is a copy defect and not a
# file that changed under the probe.
$sources = @{}
foreach ($item in $Path) {
    foreach ($name in ($item -split ',')) {
        $relative = $name.Trim()
        if (-not $relative) { continue }
        if ([System.IO.Path]::IsPathRooted($relative)) {
            Write-Host "probe worktree: name paths relative to the repository: $relative"
            exit 2
        }
        # A parent step is how a repository-relative name escapes the detached target and
        # rewrites a tracked caller file while the byte comparison still reports OK.
        # Refused here, before a worktree is created or a byte is written; a nested
        # relative name such as tools\webfoot\journal.py is unaffected.
        if (($relative -split '[\\/]') -contains '..') {
            Write-Host "probe worktree: no parent-directory step in a name path: $relative"
            exit 2
        }
        $source = Join-Path $root $relative
        if (-not (Test-Path -LiteralPath $source -PathType Leaf)) {
            Write-Host "probe worktree: no such file: $source"
            exit 2
        }
        $sources[$relative] = [pscustomobject]@{
            Path   = $source
            Sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $source).Hash
            Bytes  = (Get-Item -LiteralPath $source).Length
        }
    }
}
if ($sources.Count -eq 0) {
    Write-Host 'probe worktree: no files named'
    exit 2
}

# A detached worktree at the named commit: the probe runs the OLD tree with the
# named files copied in, which is what makes a mismatch detectable at all. With
# -VerifyOnly the target is the caller's own worktree and nothing is copied.
$parent = Join-Path $root 'build\dev-tools-test'
New-Item -ItemType Directory -Path $parent -Force | Out-Null
$created = $false
if ($VerifyOnly) {
    $target = (Resolve-Path -LiteralPath $VerifyOnly).Path
    Write-Host "probe worktree: verifying $target (nothing copied)"
} else {
    $target = Join-Path $parent ('probe-' + $commit.Substring(0, 12) + '-' + [Guid]::NewGuid().ToString('N').Substring(0, 6))
    $added = Invoke-GitCommand -Repository $root -Arguments @('worktree', 'add', '--detach', '--quiet', $target, $commit)
    if ($added.Exit -ne 0) {
        $added.Output | ForEach-Object { Write-Host "  $_" }
        Write-Host "probe worktree: git worktree add exited $($added.Exit)"
        exit $added.Exit
    }
    $created = $true
    Write-Host "probe worktree: $target (detached at $commit)"
}

$failed = $false
try {
    foreach ($relative in ($sources.Keys | Sort-Object)) {
        $source = $sources[$relative]
        $destination = Join-Path $target $relative
        # The invariant at the write itself: wherever the name resolved, the bytes may only
        # land inside the detached target.
        $insideTarget = ([System.IO.Path]::GetFullPath($destination)).StartsWith(
            ([System.IO.Path]::GetFullPath($target) + [System.IO.Path]::DirectorySeparatorChar),
            [System.StringComparison]::OrdinalIgnoreCase
        )
        if (-not $insideTarget) {
            Write-Host ("  {0,-8} {1} (outside the probe worktree)" -f 'REFUSED', $relative)
            $failed = $true
            continue
        }
        if (-not $VerifyOnly) {
            New-Item -ItemType Directory -Path (Split-Path -Parent $destination) -Force | Out-Null
            # Byte copy, never a text write: a text write is the defect this prevents.
            [System.IO.File]::Copy($source.Path, $destination, $true)
        } elseif (-not (Test-Path -LiteralPath $destination -PathType Leaf)) {
            Write-Host ("  {0,-8} {1} (not present in the probed tree)" -f 'MISSING', $relative)
            $failed = $true
            continue
        }
        $copy = [pscustomobject]@{
            Sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $destination).Hash
            Bytes  = (Get-Item -LiteralPath $destination).Length
        }
        $state = if ($copy.Sha256 -eq $source.Sha256) { 'OK' } else { 'MISMATCH' }
        if ($state -eq 'MISMATCH') { $failed = $true }
        Write-Host ("  {0,-8} {1}" -f $state, $relative)
        Write-Host ("    source sha256 {0}  {1} byte(s)" -f $source.Sha256, $source.Bytes)
        Write-Host ("    copy   sha256 {0}  {1} byte(s)" -f $copy.Sha256, $copy.Bytes)
    }
} finally {
    if ($created -and -not $Keep -and -not $failed) {
        $removed = Invoke-GitCommand -Repository $root -Arguments @('worktree', 'remove', '--force', $target)
        if ($removed.Exit -eq 0) { Write-Host 'probe worktree: removed' }
        else { Write-Host "probe worktree: could not remove $target (exit $($removed.Exit))" }
    } elseif ($failed) {
        Write-Host "probe worktree: left in place for inspection: $target"
    }
}

if ($failed) {
    Write-Host 'probe worktree: REFUSED, a copied file does not match its source'
    exit 3
}
if ($CheckOnly) { Write-Host 'probe worktree: every named file verified against its source' }
exit 0
