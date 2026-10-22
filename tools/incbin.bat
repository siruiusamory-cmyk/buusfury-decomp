@echo off
setlocal enabledelayedexpansion

if "%~3"=="" (
    echo Usage: %0 filename startHexOffset endHexOffset
    echo Example: %0 myfile.txt 0x04 0xA0
    exit /b 1
)

set "fileName=%~1"
set "startHex=%~2"
set "endHex=%~3"

if exist "!fileName!_!startHex!_!endHex!.extracted" (
    	exit /b
)

python "%~dp0extract\slice_rom.py" "!fileName!" "!startHex!" "!endHex!"
if errorlevel 1 exit /b 1


