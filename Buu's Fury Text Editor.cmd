@echo off
rem Buu's Fury Text Editor launcher - double-click to run the text editor.
rem Uses the repo venv python and always runs the current source (no rebuild).
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Could not find .venv\Scripts\python.exe next to this launcher.
    echo Create the venv and install the Qt extra first:
    echo     py -m venv .venv
    echo     .venv\Scripts\python -m pip install -e ".[packaging]"
    pause
    exit /b 1
)
start "" ".venv\Scripts\pythonw.exe" -m tools.buufury_text
endlocal
