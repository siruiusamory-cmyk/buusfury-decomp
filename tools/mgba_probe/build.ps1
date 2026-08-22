[CmdletBinding()]
param(
    [string]$SourceRoot,
    [string]$BuildRoot,
    [string]$MsysRoot,
    [switch]$CoreOnly
)

$ErrorActionPreference = 'Stop'
$SourceRoot = if ($SourceRoot) { $SourceRoot } else { Join-Path $PSScriptRoot '..\..\extern\mgba-0.10.5' }
$BuildRoot = if ($BuildRoot) {
    $BuildRoot
} elseif ($CoreOnly) {
    Join-Path $PSScriptRoot '..\..\build\rom011\mgba-probe-core'
} else {
    Join-Path $PSScriptRoot '..\..\build\rom011\mgba-probe-sdl'
}
$MsysRoot = if ($MsysRoot) { $MsysRoot } else { Join-Path $PSScriptRoot '..\..\build\rom011\deps\msys64' }

$expectedCommit = '26b7884bc25a5933960f3cdcd98bac1ae14d42e2'
$source = [System.IO.Path]::GetFullPath($SourceRoot)
$build = [System.IO.Path]::GetFullPath($BuildRoot)
$msys = [System.IO.Path]::GetFullPath($MsysRoot)
$patch = Join-Path $PSScriptRoot 'mgba-0.10.5-log1-read-probe.patch'

foreach ($required in @($source, $patch)) {
    if (-not (Test-Path -LiteralPath $required)) {
        throw "Required build input is missing: $required"
    }
}

$head = (& git -C $source rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $head -cne $expectedCommit) {
    throw "mGBA source must be pinned exactly to $expectedCommit; found $head"
}

$changed = @(& git -C $source status --porcelain)
if ($LASTEXITCODE -ne 0) { throw 'Unable to inspect mGBA source status' }
if ($changed.Count -eq 0) {
    & git -C $source apply --check $patch
    if ($LASTEXITCODE -ne 0) { throw 'Instrumentation patch does not apply cleanly to pinned source' }
    & git -C $source apply $patch
    if ($LASTEXITCODE -ne 0) { throw 'Failed to apply instrumentation patch' }
} else {
    $unexpected = @($changed | Where-Object {
        $_ -notmatch '^ M (include/mgba/internal/gba/gba.h|src/debugger/gdb-stub.c|src/gba/gba.c|src/gba/memory.c|src/gba/test/core.c)$'
    })
    if ($unexpected.Count) {
        throw "Pinned source contains unexpected changes: $($unexpected -join ', ')"
    }
    & git -C $source apply --reverse --check $patch
    if ($LASTEXITCODE -ne 0) { throw 'Existing source changes do not exactly contain the tracked probe patch' }
}

& git -C $source diff --check
if ($LASTEXITCODE -ne 0) { throw 'Patched mGBA source fails git diff --check' }

$commonConfigure = @(
    '-S', $source, '-B', $build,
    '-DCMAKE_POLICY_VERSION_MINIMUM=3.5', '-DCMAKE_BUILD_TYPE=Release',
    '-DBUILD_QT=OFF', '-DBUILD_TEST=OFF', '-DBUILD_SUITE=OFF',
    '-DBUILD_CINEMA=OFF', '-DBUILD_EXAMPLE=OFF', '-DBUILD_PERF=OFF',
    '-DBUILD_LTO=OFF', '-DUSE_DISCORD_RPC=OFF',
    '-DENABLE_SCRIPTING=OFF', '-DUSE_GDB_STUB=ON', '-DUSE_FFMPEG=OFF',
    '-DUSE_SQLITE3=OFF', '-DUSE_ELF=OFF', '-DUSE_LIBZIP=OFF',
    '-DUSE_MINIZIP=OFF'
)

if ($CoreOnly) {
    $cmake = 'C:\Program Files\CMake\bin\cmake.exe'
    $vsDevCmd = 'C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\Common7\Tools\VsDevCmd.bat'
    foreach ($required in @($cmake, $vsDevCmd)) {
        if (-not (Test-Path -LiteralPath $required)) { throw "Required core-check input is missing: $required" }
    }
    $environmentCommand = "`"$vsDevCmd`" -no_logo -arch=x64 && set"
    $environmentLines = & $env:ComSpec /d /s /c $environmentCommand
    if ($LASTEXITCODE -ne 0) { throw 'Visual Studio developer environment initialization failed' }
    foreach ($line in $environmentLines) {
        if ($line -match '^([^=]+)=(.*)$') {
            [Environment]::SetEnvironmentVariable($Matches[1], $Matches[2], 'Process')
        }
    }
    $configure = $commonConfigure + @(
        '-G', 'NMake Makefiles', '-DBUILD_SDL=OFF', '-DLIBMGBA_ONLY=ON',
        '-DUSE_ZLIB=OFF', '-DUSE_PNG=OFF', '-DBUILD_GL=OFF',
        '-DBUILD_GLES2=OFF', '-DBUILD_GLES3=OFF'
    )
    & $cmake @configure
    if ($LASTEXITCODE -ne 0) { throw 'mGBA core CMake configuration failed' }
    & $cmake --build $build
    if ($LASTEXITCODE -ne 0) { throw 'mGBA core build failed' }

    $gdbObject = Join-Path $build 'gdb-stub-probe-check.obj'
    $gdbCompile = @(
        '/nologo', '/c', '/std:c11', '/W3', '/DWIN32', '/D_WINDOWS',
        '/D_CRT_SECURE_NO_WARNINGS', '/wd4003', '/wd4244', '/wd4146', '/wd4267',
        '/Zc:preprocessor-', '/MD', '/O2', '/Ob2', '/DNDEBUG', '/DBUILD_STATIC',
        '/DHAVE_SETLOCALE', '/DHAVE_STRDUP', '/DM_CORE_GB', '/DM_CORE_GBA',
        '/DNOMINMAX', '/DUNICODE', '/DUSE_DEBUGGERS', '/DUSE_GDB_STUB',
        '/DWIN32_LEAN_AND_MEAN', '/D_UNICODE', '/D_WIN32_WINNT=0x0600',
        "/I$source\include", "/I$build\include", "/I$source\src",
        "/Fo$gdbObject", (Join-Path $source 'src\debugger\gdb-stub.c')
    )
    & cl.exe @gdbCompile
    if ($LASTEXITCODE -ne 0) { throw 'Instrumented GDB transport compile check failed' }
    Write-Host "Pinned instrumented core build succeeded: $build"
    exit 0
}

$mingwBin = Join-Path $msys 'mingw64\bin'
$cmake = Join-Path $mingwBin 'cmake.exe'
$ninja = Join-Path $mingwBin 'ninja.exe'
$gcc = Join-Path $mingwBin 'gcc.exe'
$gxx = Join-Path $mingwBin 'g++.exe'
$pkgConfig = Join-Path $mingwBin 'pkg-config.exe'
$pacman = Join-Path $msys 'usr\bin\pacman.exe'
foreach ($required in @($cmake, $ninja, $gcc, $gxx, $pkgConfig, $pacman, (Join-Path $mingwBin 'SDL2.dll'), (Join-Path $mingwBin 'libepoxy-0.dll'))) {
    if (-not (Test-Path -LiteralPath $required)) { throw "Isolated MSYS2 build input is missing: $required" }
}
$env:Path = "$mingwBin;$env:Path"
$configure = $commonConfigure + @(
    '-G', 'Ninja', "-DCMAKE_MAKE_PROGRAM=$ninja",
    "-DCMAKE_C_COMPILER=$gcc", "-DCMAKE_CXX_COMPILER=$gxx",
    '-DBUILD_SDL=ON', '-DBUILD_STATIC=ON', '-DBUILD_SHARED=OFF',
    '-DUSE_EPOXY=ON', '-DUSE_ZLIB=ON', '-DUSE_PNG=ON'
)
& $cmake @configure
if ($LASTEXITCODE -ne 0) { throw 'Playable mGBA CMake configuration failed' }
& $cmake --build $build --target mgba-sdl
if ($LASTEXITCODE -ne 0) { throw 'Playable mGBA SDL build failed' }

$executable = Join-Path $build 'mgba-sdl.exe'
if (-not (Test-Path -LiteralPath $executable)) { throw "Expected SDL executable was not produced: $executable" }
$version = (& $executable --version | Out-String).Trim()
if ($version -notmatch '0\.10\.5' -or $version -notmatch $expectedCommit.Substring(0, 8)) {
    throw "Built executable version is not pinned mGBA 0.10.5: $version"
}

$packages = @(
    'mingw-w64-x86_64-gcc', 'mingw-w64-x86_64-cmake',
    'mingw-w64-x86_64-ninja', 'mingw-w64-x86_64-pkgconf',
    'mingw-w64-x86_64-SDL2', 'mingw-w64-x86_64-libepoxy',
    'mingw-w64-x86_64-libpng', 'mingw-w64-x86_64-zlib'
)
$packageVersions = [ordered]@{}
foreach ($line in @(& $pacman -Q @packages)) {
    $name, $versionNumber = $line -split ' ', 2
    $packageVersions[$name] = $versionNumber
}
$manifest = [ordered]@{
    schema = 'log1-mgba-instrumented-build-v1'
    source_commit = $expectedCommit
    patch_sha256 = (Get-FileHash -LiteralPath $patch -Algorithm SHA256).Hash.ToLowerInvariant()
    compiler = (& $gcc --version | Select-Object -First 1)
    cmake = (& $cmake --version | Select-Object -First 1)
    generator = 'Ninja'
    frontend = "SDL2 $(& $pkgConfig --modversion sdl2) x64"
    libepoxy = (& $pkgConfig --modversion epoxy)
    packages = $packageVersions
    runtime_bin = $mingwBin
    build_options = @('BUILD_QT=OFF', 'BUILD_SDL=ON', 'BUILD_STATIC=ON', 'BUILD_SHARED=OFF', 'BUILD_LTO=OFF', 'ENABLE_SCRIPTING=OFF', 'USE_GDB_STUB=ON', 'USE_DISCORD_RPC=OFF', 'USE_EPOXY=ON', 'USE_ZLIB=ON', 'USE_PNG=ON')
    executable = $executable
    executable_sha256 = (Get-FileHash -LiteralPath $executable -Algorithm SHA256).Hash.ToLowerInvariant()
    version_output = $version
}
$manifestPath = Join-Path $build 'log1-probe-build.json'
$json = $manifest | ConvertTo-Json -Depth 5
[System.IO.File]::WriteAllText($manifestPath, $json + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
Write-Host "Instrumented mGBA: $executable"
Write-Host "Build manifest: $manifestPath"
