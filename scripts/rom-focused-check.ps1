# A focused ROM run: the tests named by config/rom-dependent-tests.txt, against a
# private copy of the canonical image.
#
# Why a staging tree and not just environment variables. Two spellings resolve the
# image. The tests/rom_support.py family honours WEBFOOT_BUU_ROM and
# LOGX_CANONICAL_ROM and then falls back to <repo>\roms. The 19 DragonByte modules
# instead glob a sibling checkout derived from their own __file__:
# tests/unit/dragonbyte_acceptance_support.py resolves
# `Path(__file__).resolve().parents[2].parent / "log1-remake"`. From a ticket
# worktree that sibling is the real primary checkout, so a run that only set
# environment variables would read the canonical image in place, and on this
# machine that file is a hard link shared with other worktrees: the R3 class.
# This script therefore stages a tree in which BOTH spellings land on copies.
#
# What it builds, under the ignored <repo>\build\rom-focused\<stamp>\:
#   rt\                      a detached git worktree at HEAD, the tree under test
#   rt\roms\<name>           a private byte copy, for the relative-roms readers
#   log1-remake\roms\<name>  a second private byte copy, for the sibling readers
# Two independent byte copies. Nothing here is hard-linked, symlinked or
# junctioned, each copy is digest-verified and each is proved a DISTINCT file from
# the image by file identity, the way tests/rom_support.py does it.
#
# Contract, per docs/ROM_SAFETY.md:
#   - the canonical image is READ ONLY: never written, staged, moved, linked or
#     deleted, and its sha256 is checked before and after the run;
#   - every destination is refused when it already exists, because a pre-existing
#     name may be a link to the image and writing through it is the R3 bug;
#   - fail closed on no image, a non-canonical digest, a missing or empty
#     inventory, no python on PATH, a staging sibling that is not this run's own
#     copy, an existing destination, a copy that is not a distinct file, or a
#     digest that moved;
#   - a run that executed zero nodes is a failure: an all-skipped run is not
#     evidence, and the residual reasons are printed, including the ones this
#     staging tree cannot satisfy (the assembled atlas index, the release-4A
#     image, the instrumented emulator builds);
#   - the staging tree is removed afterwards unless -KeepCopy is passed.
#
# No emulator is started, no save state is loaded, nothing is installed and
# nothing reaches the network. The selection is the inventory's own file paths: a
# focused run, never a directory and never the whole suite.

[CmdletBinding()]
param(
    # The canonical image. Default: WEBFOOT_BUU_ROM, then LOGX_CANONICAL_ROM, then
    # <repo>\roms\<the canonical name>. Always checked against the canonical digest.
    [string]$Image,

    # The repository under test. Default: the repository this script lives in.
    # Resolved in the body, not here: Windows PowerShell 5.1 has no $PSScriptRoot
    # yet while it binds parameter defaults.
    [string]$RepoPath,

    # The test files to run. Default: the inventory's own lines.
    [string[]]$FocusFiles,

    # Where the staging tree goes. Must sit under this repository's build\, so it
    # is ignored. Default: a fresh unique directory there.
    [string]$StagingRoot,

    # Keep the staging tree and its copies. The default removes them.
    [switch]$KeepCopy
)

$ErrorActionPreference = 'Stop'

$CanonicalSha256 = '940AD5F01DB4465B8877DFE739510CBF34F4EA3D390F3DF13519808BC36F059E'
$ImageName = "Dragon Ball Z - Buu's Fury (U).gba"

function Stop-FocusedRun {
    param([string]$Reason)
    throw "rom-focused-check: $Reason"
}

function Get-Digest {
    param([string]$Path)
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash
}

function Assert-CanonicalImage {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        Stop-FocusedRun "the image $Path does not exist"
    }
    $digest = Get-Digest -Path $Path
    if ($digest -ne $CanonicalSha256) {
        Stop-FocusedRun ("the image $Path is not the canonical image: sha256 $digest, expected " +
            "$CanonicalSha256")
    }
    return $digest
}

function Assert-DistinctFromImage {
    # File identity, as tests/rom_support.py measures it: device and file index.
    # A copy that shares them IS the image under another name, however it was named.
    param([string]$Copy, [string]$ImagePath, [string]$PythonPath)
    $probe = ('import os, sys; a = os.stat(sys.argv[1]); b = os.stat(sys.argv[2]); ' +
        'sys.exit(3 if (a.st_dev, a.st_ino) == (b.st_dev, b.st_ino) else 0)')
    & $PythonPath -c $probe $Copy $ImagePath
    if ($LASTEXITCODE -eq 3) {
        Stop-FocusedRun ("$Copy is the same file as the image $ImagePath under another name, which " +
            'is a link and not a private copy')
    }
    if ($LASTEXITCODE -ne 0) {
        Stop-FocusedRun "the file-identity probe on $Copy exited $LASTEXITCODE"
    }
}

function New-PrivateCopy {
    # One byte copy, in a destination that did not exist. The existing-destination
    # check comes first and is the point: Copy-Item writes THROUGH an existing
    # name, so if that name were a link to the image this would edit the image.
    param([string]$Destination, [string]$ImagePath, [string]$PythonPath)
    if (Test-Path -LiteralPath $Destination) {
        Stop-FocusedRun ("the destination $Destination already exists, so this run refuses to write " +
            'through it: a pre-existing name may be a link to the canonical image')
    }
    $parent = Split-Path -Parent $Destination
    if (-not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Force -Path $parent | Out-Null
    }
    Copy-Item -LiteralPath $ImagePath -Destination $Destination
    $item = Get-Item -LiteralPath $Destination -Force
    if ($item.LinkType) {
        Stop-FocusedRun "$Destination is a $($item.LinkType), not an independent byte copy"
    }
    $digest = Get-Digest -Path $Destination
    if ($digest -ne $CanonicalSha256) {
        Stop-FocusedRun "the copy $Destination is not byte-equal to the canonical image (sha256 $digest)"
    }
    Assert-DistinctFromImage -Copy $Destination -ImagePath $ImagePath -PythonPath $PythonPath
    Write-Output "rom-focused-check: copy $Destination sha256 $digest, a distinct file from the image"
}

function Write-NodeCounts {
    param([string]$ReportPath, [string[]]$Files)
    $script:ExecutedNodes = 0
    if (-not (Test-Path -LiteralPath $ReportPath -PathType Leaf)) {
        Write-Output "rom-focused-check: no junit report at $ReportPath, so nothing can be counted"
        return
    }
    [xml]$report = Get-Content -LiteralPath $ReportPath -Raw
    $cases = @($report.SelectNodes('//testcase'))
    $counts = @{}
    foreach ($case in $cases) {
        $file = $case.file
        if (-not $file) { $file = ($case.classname -replace '\.', '/') + '.py' }
        $file = $file.Replace('\', '/')
        if (-not $counts.ContainsKey($file)) {
            $counts[$file] = @{ Executed = 0; Skipped = 0; Reasons = @() }
        }
        $skip = $case.SelectSingleNode('skipped')
        if ($skip) {
            $counts[$file].Skipped++
            $reason = $skip.GetAttribute('message')
            if (-not $reason) { $reason = 'no reason recorded' }
            $counts[$file].Reasons += $reason
        }
        else {
            $counts[$file].Executed++
        }
    }
    $executed = 0
    $skipped = 0
    foreach ($file in $Files) {
        $key = $file.Replace('\', '/')
        if (-not $counts.ContainsKey($key)) {
            Write-Output "rom-focused-check: $key collected no node at all"
            continue
        }
        $entry = $counts[$key]
        $executed += $entry.Executed
        $skipped += $entry.Skipped
        Write-Output ("rom-focused-check: $key executed {0}, skipped {1}" -f $entry.Executed, $entry.Skipped)
    }
    $reasons = @{}
    foreach ($file in $counts.Keys) {
        foreach ($reason in $counts[$file].Reasons) {
            if (-not $reasons.ContainsKey($reason)) { $reasons[$reason] = @() }
            if ($reasons[$reason] -notcontains $file) { $reasons[$reason] += $file }
        }
    }
    foreach ($reason in ($reasons.Keys | Sort-Object)) {
        Write-Output ("rom-focused-check: still skipping for: {0} ({1} file(s): {2})" -f `
                $reason, $reasons[$reason].Count, ($reasons[$reason] -join ', '))
    }
    Write-Output "rom-focused-check: executed $executed node(s), skipped $skipped node(s)"
    $script:ExecutedNodes = $executed
}

# --- what to run, from the inventory ------------------------------------------
if (-not $RepoPath) {
    $RepoPath = Split-Path -Parent $PSScriptRoot
}
if (-not (Test-Path -LiteralPath (Join-Path $RepoPath '.git'))) {
    Stop-FocusedRun "$RepoPath is not the root of a git worktree, so no staging worktree can be made"
}
$inventoryPath = Join-Path $RepoPath 'config/rom-dependent-tests.txt'
if (-not (Test-Path -LiteralPath $inventoryPath -PathType Leaf)) {
    Stop-FocusedRun "config/rom-dependent-tests.txt is missing from ${RepoPath}: the inventory is the run"
}
$inventory = @(Get-Content -LiteralPath $inventoryPath |
    ForEach-Object { $_.Trim() } |
    Where-Object { $_ -and -not $_.StartsWith('#') })
if ($inventory.Count -eq 0) {
    Stop-FocusedRun "config/rom-dependent-tests.txt in ${RepoPath} names no test file, so there is nothing to run"
}
if (-not $FocusFiles -or $FocusFiles.Count -eq 0) {
    $FocusFiles = $inventory
}

# --- the staging tree's shape, before anything is created ---------------------
if ($StagingRoot) {
    $stagingFull = [System.IO.Path]::GetFullPath($StagingRoot)
    $buildFull = [System.IO.Path]::GetFullPath((Join-Path $RepoPath 'build'))
    if (-not $stagingFull.StartsWith($buildFull + [System.IO.Path]::DirectorySeparatorChar,
            [System.StringComparison]::OrdinalIgnoreCase)) {
        Stop-FocusedRun "the staging root $StagingRoot is not under ${RepoPath}\build, which is the ignored tree"
    }
}
else {
    $StagingRoot = Join-Path $RepoPath ('build\rom-focused\' + (Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
}
$rtPath = Join-Path $StagingRoot 'rt'
$siblingRoms = Join-Path $StagingRoot 'log1-remake\roms'
$rtRoms = Join-Path $rtPath 'roms'
$siblingCopy = Join-Path $siblingRoms $ImageName
$rtCopy = Join-Path $rtRoms $ImageName

# Every destination is refused when it already exists: a pre-existing name may be
# a link to the canonical image, and copying through one would edit the image.
foreach ($destination in @($siblingCopy, $rtCopy)) {
    if (Test-Path -LiteralPath $destination) {
        Stop-FocusedRun ("the destination $destination already exists, so this run refuses to write " +
            'through it: a pre-existing name may be a link to the canonical image')
    }
}
# A staging sibling that holds anything else is refused by name: the DragonByte
# lookup reads that directory, and a file this run did not make could be picked up.
if (Test-Path -LiteralPath $siblingRoms) {
    $preoccupied = @(Get-ChildItem -LiteralPath $siblingRoms -File -Force)
    if ($preoccupied.Count -gt 0) {
        Stop-FocusedRun ("the staging sibling $siblingRoms already holds $($preoccupied[0].Name), so it " +
            'is not a staging tree whose sibling resolves to this run''s own copy of the canonical image')
    }
}

# --- the image, read-only -----------------------------------------------------
if (-not $Image) {
    foreach ($candidate in @($env:WEBFOOT_BUU_ROM, $env:LOGX_CANONICAL_ROM,
            (Join-Path $RepoPath (Join-Path 'roms' $ImageName)))) {
        if ($candidate -and (Test-Path -LiteralPath $candidate -PathType Leaf)) {
            $Image = $candidate
            break
        }
    }
}
if (-not $Image) {
    Stop-FocusedRun ('no canonical image: pass -Image, or set WEBFOOT_BUU_ROM or LOGX_CANONICAL_ROM, ' +
        'or place the image under the repository roms\ directory')
}
$imageBefore = Assert-CanonicalImage -Path $Image
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Stop-FocusedRun 'no python on PATH: the focused run needs the interpreter that carries the test suite'
}
$pythonPath = $python.Source

# --- build the staging tree ---------------------------------------------------
if (-not (Test-Path -LiteralPath $StagingRoot)) {
    New-Item -ItemType Directory -Force -Path $StagingRoot | Out-Null
}
$head = (@(& git -C $RepoPath rev-parse HEAD 2>&1) | Select-Object -First 1).ToString().Trim()
if ($LASTEXITCODE -ne 0) { Stop-FocusedRun "git rev-parse HEAD failed in ${RepoPath}: $head" }
if (Test-Path -LiteralPath $rtPath) {
    Stop-FocusedRun "the staging worktree $rtPath already exists, so this run refuses to reuse it"
}
# Not captured: git writes its progress to stderr, and redirecting a native
# command's stderr into the pipeline is a terminating error under `Stop`.
& git -C $RepoPath worktree add --detach $rtPath $head
if ($LASTEXITCODE -ne 0) {
    Stop-FocusedRun "git worktree add failed for $rtPath at $head"
}
Write-Output "rom-focused-check: staging worktree $rtPath at $head"

# Two independent byte copies: the sibling the DragonByte modules glob, and the
# repository-relative one the tests/rom_support.py fallback reads.
New-PrivateCopy -Destination $siblingCopy -ImagePath $Image -PythonPath $pythonPath
$siblingDigest = Get-Digest -Path $siblingCopy
New-PrivateCopy -Destination $rtCopy -ImagePath $Image -PythonPath $pythonPath
$rtDigest = Get-Digest -Path $rtCopy
$siblingFound = @(Get-ChildItem -LiteralPath $siblingRoms -Filter *.gba -File |
    Where-Object { (Get-Digest -Path $_.FullName) -eq $CanonicalSha256 })
if ($siblingFound.Count -ne 1) {
    Stop-FocusedRun ("$siblingRoms resolves to $($siblingFound.Count) canonical-digest image(s), and the " +
        'sibling lookup the DragonByte modules make needs exactly this run''s copy')
}
Write-Output ("rom-focused-check: sibling lookup $siblingRoms resolves to $($siblingFound[0].FullName) " +
    "sha256 $CanonicalSha256")

# --- the run ------------------------------------------------------------------
$reportPath = Join-Path $StagingRoot 'rom-focused-report.xml'
$previousWebfoot = $env:WEBFOOT_BUU_ROM
$previousLogx = $env:LOGX_CANONICAL_ROM
$childExit = 1
Push-Location -LiteralPath $rtPath
try {
    # For the child only. The caller's environment is restored below.
    $env:WEBFOOT_BUU_ROM = $rtCopy
    $env:LOGX_CANONICAL_ROM = $rtCopy
    Write-Output ("rom-focused-check: python -m pytest " + ($FocusFiles -join ' ') +
        " -q --junitxml=$reportPath")
    & $pythonPath -m pytest $FocusFiles -q "--junitxml=$reportPath"
    $childExit = $LASTEXITCODE
}
finally {
    Pop-Location
    $env:WEBFOOT_BUU_ROM = $previousWebfoot
    $env:LOGX_CANONICAL_ROM = $previousLogx
}
Write-Output "rom-focused-check: the child run exited $childExit"

# --- digests after, then the counts -------------------------------------------
$imageAfter = Get-Digest -Path $Image
Write-Output "rom-focused-check: image $Image sha256 before $imageBefore, after $imageAfter"
if ($imageAfter -ne $imageBefore) {
    Stop-FocusedRun "the canonical image $Image moved during this run (before $imageBefore, after $imageAfter)"
}
$siblingAfter = Get-Digest -Path $siblingCopy
$rtAfter = Get-Digest -Path $rtCopy
if ($siblingAfter -ne $siblingDigest -or $rtAfter -ne $rtDigest) {
    Stop-FocusedRun ("a private copy moved during this run: sibling before $siblingDigest after " +
        "$siblingAfter; worktree before $rtDigest after $rtAfter")
}
Write-Output "rom-focused-check: sibling copy sha256 $siblingAfter; worktree copy sha256 $rtAfter"

Write-NodeCounts -ReportPath $reportPath -Files $FocusFiles
$executed = $script:ExecutedNodes

# --- cleanup ------------------------------------------------------------------
if ($KeepCopy) {
    Write-Output "rom-focused-check: -KeepCopy, so $StagingRoot is kept"
}
else {
    Write-Output ("rom-focused-check: removing $StagingRoot; the worktree copy was $rtAfter and the " +
        "sibling copy was $siblingAfter")
    & git -C $RepoPath worktree remove --force $rtPath
    if ($LASTEXITCODE -ne 0) {
        Write-Output "rom-focused-check: git worktree remove failed for $rtPath; leaving $StagingRoot in place"
    }
    else {
        Remove-Item -LiteralPath $StagingRoot -Recurse -Force
        Write-Output "rom-focused-check: removed $StagingRoot"
    }
}

if ($childExit -ne 0) {
    Write-Output "rom-focused-check: FAIL, the focused run exited $childExit"
    exit 1
}
if ($executed -eq 0) {
    Write-Output ('rom-focused-check: FAIL, no node executed: a run that only skipped is not evidence, ' +
        'and the reasons are listed above')
    exit 1
}
Write-Output "rom-focused-check: PASS, $executed node(s) executed against a private copy"
exit 0
