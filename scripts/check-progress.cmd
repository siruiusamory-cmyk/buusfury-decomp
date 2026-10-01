@echo off
:: Closeout check for the decomp.dev semantic progress report.
:: See scripts\check-progress.ps1 for the full description.
::
:: Every completed decomp ticket that changes reconstruction state runs this
:: before commit/closeout. It is a targeted infrastructure check, not a test
:: suite, and it needs no ROM, no compiler and no build.
::
::   scripts\check-progress.cmd
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0check-progress.ps1" %*
exit /b %ERRORLEVEL%
