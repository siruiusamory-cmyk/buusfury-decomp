@echo off
:: Build build\buusfury.gba. See scripts\build.ps1 for the full description.
::
:: Strict by default: fails closed on any region it cannot rebuild.
::   build.cmd                      strict; stops with the precise ADS blocker
::   build.cmd -AllowPassthrough    assemble anyway, with a labelled report
::
:: Delegates to Windows PowerShell 5.1 (present on every Windows machine).
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0build.ps1" %*
exit /b %ERRORLEVEL%
