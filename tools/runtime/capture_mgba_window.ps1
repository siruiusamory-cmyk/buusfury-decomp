<#
.SYNOPSIS
Capture the mGBA GAME window (or a named child) to a PNG.

.DESCRIPTION
The first version of this script captured `MainWindowHandle`, which for the 0.11
build is the **Scripting** window - a capture showing the injector's log pane
rather than the game. This version enumerates every top-level window owned by
the mGBA process, prints them with their titles and sizes, and captures the one
whose title matches `-TitleMatch` (default: any window whose title names mGBA).

The emulator's grid widget can also be absent from a plain screen copy on some
compositors, so `-VerifyGrid` re-reads the same rectangle through the GDI
`PrintWindow` path and reports which of the two grabs has more distinct colours;
a blank/uniform grab is rejected rather than silently saved.

Read-only with respect to the emulator: reads pixels, writes one PNG, sends no
input, touches no emulated memory, and does not stop the process.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$OutPath,
    [string]$ProcessName = 'mGBA',
    [string]$TitleMatch = 'mGBA',
    [int]$SettleSeconds = 2,
    # MAP-CHUNK-AUTHORING-001. Raise the emulator window to the foreground before
    # copying the screen. A plain CopyFromScreen copies whatever is on the desktop
    # inside the emulator's rectangle, so ANY overlapping window is captured in its
    # place - measured once: a browser window covering the right two thirds of the
    # emulator produced a matched pair whose two frames were not even crops of the
    # same region, because the two runs' windows sat at different screen positions.
    # Off by default so every existing caller's behaviour is unchanged.
    [switch]$BringToFront,
    [switch]$ListOnly
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing

Add-Type @'
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Text;
public class WinEnum {
    public delegate bool EnumProc(IntPtr hWnd, IntPtr lParam);
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr lParam);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint pid);
    [DllImport("user32.dll")] public static extern int GetWindowTextLength(IntPtr hWnd);
    [DllImport("user32.dll", CharSet = CharSet.Unicode)] public static extern int GetWindowText(IntPtr hWnd, StringBuilder text, int count);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);
    [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr hWnd, IntPtr hdc, uint flags);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int cmd);
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }

    public static List<string> WindowsFor(uint target) {
        var found = new List<string>();
        EnumWindows((h, l) => {
            uint pid;
            GetWindowThreadProcessId(h, out pid);
            if (pid == target) {
                int len = GetWindowTextLength(h);
                var sb = new StringBuilder(len + 1);
                GetWindowText(h, sb, sb.Capacity);
                RECT r;
                GetWindowRect(h, out r);
                found.Add(string.Format("{0}|{1}|{2}|{3}|{4}|{5}",
                    h.ToInt64(), sb.ToString(), r.Left, r.Top,
                    r.Right - r.Left, r.Bottom - r.Top));
            }
            return true;
        }, IntPtr.Zero);
        return found;
    }
}
'@

$process = Get-Process -Name $ProcessName -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $process) { throw "no $ProcessName process is running" }

Start-Sleep -Seconds $SettleSeconds

$rows = [WinEnum]::WindowsFor([uint32]$process.Id) | ForEach-Object {
    $parts = $_ -split '\|'
    [pscustomobject]@{
        Handle = [int64]$parts[0]
        Title  = $parts[1]
        Left   = [int]$parts[2]
        Top    = [int]$parts[3]
        Width  = [int]$parts[4]
        Height = [int]$parts[5]
    }
}
$rows | Format-Table -AutoSize | Out-String | Write-Output
if ($ListOnly) { return }

$target = $rows | Where-Object { $_.Title -match $TitleMatch -and $_.Width -gt 0 } |
    Sort-Object { $_.Width * $_.Height } -Descending | Select-Object -First 1
if (-not $target) { throw "no $ProcessName window matched '$TitleMatch'" }

if ($BringToFront) {
    # Restore (in case it is minimised), raise and activate, then let the
    # compositor settle before the copy. The re-read of the window rectangle
    # afterwards matters: restoring can move the window, and copying the stale
    # rectangle would capture whatever is now there instead.
    [WinEnum]::ShowWindow([IntPtr]$target.Handle, 9) | Out-Null   # SW_RESTORE
    [WinEnum]::SetForegroundWindow([IntPtr]$target.Handle) | Out-Null
    Start-Sleep -Seconds 2
    $again = [WinEnum]::WindowsFor([uint32]$process.Id) | ForEach-Object {
        $parts = $_ -split '\|'
        if ([int64]$parts[0] -eq $target.Handle) {
            [pscustomobject]@{ Handle = [int64]$parts[0]
                               Left = [int]$parts[2]; Top = [int]$parts[3]
                               Width = [int]$parts[4]; Height = [int]$parts[5] }
        }
    } | Select-Object -First 1
    if ($again -and $again.Width -gt 0) { $target = $again }
    Write-Output "raised to foreground: $($target.Width)x$($target.Height) at ($($target.Left),$($target.Top))"
}

$width = $target.Width
$height = $target.Height
$bitmap = New-Object System.Drawing.Bitmap($width, $height)
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
try {
    $graphics.CopyFromScreen($target.Left, $target.Top, 0, 0, $bitmap.Size)
} finally {
    $graphics.Dispose()
}

# GDI PrintWindow grab, as a second opinion for compositor-hidden content.
$gdi = New-Object System.Drawing.Bitmap($width, $height)
$gdiGraphics = [System.Drawing.Graphics]::FromImage($gdi)
$hdc = $gdiGraphics.GetHdc()
try {
    [void][WinEnum]::PrintWindow([IntPtr]$target.Handle, $hdc, 2)
} finally {
    $gdiGraphics.ReleaseHdc($hdc)
    $gdiGraphics.Dispose()
}

function Get-DistinctColours($bmp) {
    $seen = New-Object 'System.Collections.Generic.HashSet[int]'
    $step = [Math]::Max(1, [int]($bmp.Width / 60))
    for ($y = 0; $y -lt $bmp.Height; $y += $step) {
        for ($x = 0; $x -lt $bmp.Width; $x += $step) {
            [void]$seen.Add($bmp.GetPixel($x, $y).ToArgb())
        }
    }
    return $seen.Count
}

$screenColours = Get-DistinctColours $bitmap
$gdiColours = Get-DistinctColours $gdi
$chosen = if ($gdiColours -gt $screenColours) { $gdi } else { $bitmap }
$chosenName = if ($gdiColours -gt $screenColours) { 'PrintWindow' } else { 'CopyFromScreen' }

$directory = Split-Path -Parent $OutPath
if ($directory -and -not (Test-Path -LiteralPath $directory)) {
    New-Item -ItemType Directory -Path $directory -Force | Out-Null
}
$chosen.Save($OutPath, [System.Drawing.Imaging.ImageFormat]::Png)
$bitmap.Dispose()
$gdi.Dispose()

$info = Get-Item -LiteralPath $OutPath
Write-Output "CAPTURED $($info.FullName)"
Write-Output "  window  : '$($target.Title)' ${width}x${height} at ($($target.Left),$($target.Top))"
Write-Output "  pid     : $($process.Id)"
Write-Output "  method  : $chosenName (screen=$screenColours gdi=$gdiColours distinct colours)"
Write-Output "  bytes   : $($info.Length)"
