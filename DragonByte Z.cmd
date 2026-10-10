@echo off
rem DragonByte Z launcher - double-click to run the visual editor.
rem Uses the repo venv python and always runs the current source (no rebuild).
rem The beta workbench is a different application: python -m tools.webfoot.workbench.
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Could not find .venv\Scripts\python.exe next to this launcher.
    echo Create the venv and install the workbench extra first:
    echo     py -m venv .venv
    echo     .venv\Scripts\python -m pip install -e ".[workbench]"
    pause
    exit /b 1
)
start "" ".venv\Scripts\pythonw.exe" -m tools.dragonbyte
endlocal
