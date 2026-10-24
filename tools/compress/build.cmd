@echo off
setlocal
set "HERE=%~dp0"
set "CMAKE="
set "VSWHERE=%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe"
if exist "%VSWHERE%" for /f "usebackq delims=" %%i in (`"%VSWHERE%" -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -find Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe`) do set "CMAKE=%%i"
if not defined CMAKE set "CMAKE=cmake"
"%CMAKE%" -B "%HERE%build" -A Win32 "%HERE%." || exit /b 1
"%CMAKE%" --build "%HERE%build" --config Release || exit /b 1
copy /Y "%HERE%build\Release\compress.exe" "%HERE%compress.exe" >nul || exit /b 1
