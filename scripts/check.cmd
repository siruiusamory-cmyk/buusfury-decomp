@echo off
:: One-command baseline check. See scripts\check.ps1 for the full description.
::
:: Delegates to Windows PowerShell 5.1, which is present on every Windows
:: machine. PowerShell 7 (pwsh) is NOT installed on the development machine, so
:: the scripts are written to run on 5.1 or later.
::
::   check.cmd                          use .\baserom.gba
::   check.cmd -Rom D:\roms\buu.gba     explicit baserom
::   check.cmd -SkipTests               skip the pytest gate
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0check.ps1" %*
exit /b %ERRORLEVEL%
