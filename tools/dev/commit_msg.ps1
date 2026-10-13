# Write a commit message as UTF-8 with NO byte-order mark and pass it to
# `git commit -F`. Two measured failures made this a tool rather than a habit
# (dbz-dev retro 1.7): a here-string carrying double quotes was split by native
# argument passing and git read it as a pathspec, and `Set-Content -Encoding utf8`
# writes a BOM that lands inside the first commit-message line.
#
# The hook's rules, stated here because the tool cannot enforce them for you:
#   * no em dash in a staged .md or .txt file;
#   * the subject describes the change itself, not the cleanup process that
#     produced it ("Add the one-writer sweep", not "clean up the retro items").
#
# Usage:
#   powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\dev\commit_msg.ps1 `
#       -Message 'Add the one-writer sweep' -Path scripts\new-ticket-worktree.ps1
#   ... -Message (Get-Content -Raw message.txt)    # multi-line, quotes and all
#   ... -Message '...' -NoCommit                   # write the message file only
#
# -NoCommit prints the message file path and exits 0 without running git, which
# is how the guard proves the no-BOM and verbatim claims.
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Message,
    [string[]]$Path = @(),
    [string]$MessageFile,
    [switch]$NoCommit
)

$ErrorActionPreference = 'Stop'
$root = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path

# `git commit -F` strips trailing newlines but not leading ones, and an all-blank
# message reaches git as "empty commit message" only after the editor is skipped,
# so the refusal is here where it can name the caller's mistake.
if (-not $Message -or -not $Message.Trim()) {
    throw 'commit_msg.ps1: the message is empty; there is nothing to commit with'
}

if (-not $MessageFile) {
    $MessageFile = Join-Path ([System.IO.Path]::GetTempPath()) ('log1-commit-msg-' + [Guid]::NewGuid().ToString('N') + '.txt')
}

# The one line that carries the measured trap: .NET writes exactly the bytes given,
# where every PowerShell encoding spelling on 5.1 either has no name (utf8NoBOM) or
# writes a BOM (utf8).
[System.IO.File]::WriteAllText($MessageFile, $Message, (New-Object System.Text.UTF8Encoding($false)))

$head = [System.IO.File]::ReadAllBytes($MessageFile) | Select-Object -First 3
$hasBom = $head.Count -eq 3 -and $head[0] -eq 0xEF -and $head[1] -eq 0xBB -and $head[2] -eq 0xBF
if ($hasBom) {
    throw "commit_msg.ps1: wrote a byte-order mark into $MessageFile"
}

if ($NoCommit) {
    Write-Host "message written: $MessageFile (no BOM, $([System.IO.File]::ReadAllBytes($MessageFile).Length) bytes)"
    exit 0
}

$arguments = @('commit', '-F', $MessageFile)
if ($Path.Count -gt 0) { $arguments += @('--') + $Path }

$ErrorActionPreference = 'Continue'
try {
    & git -C $root @arguments
    $exit = $LASTEXITCODE
} finally {
    $ErrorActionPreference = 'Stop'
}
if ($exit -ne 0) { throw "git commit exited $exit" }
exit 0
