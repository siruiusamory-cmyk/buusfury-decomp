@echo off
setlocal
set "ROOT=%~dp0"
if "%ROOT:~-1%"=="\" set "ROOT=%ROOT:~0,-1%"
if not "%CLANG_FORMAT%"=="" set "CF=%CLANG_FORMAT%"
if "%CF%"=="" set "CF=clang-format"
set "CF=%CF:"=%"
for %%d in (src include) do (
    for /r "%ROOT%\%%d" %%f in (*.c *.cpp *.h *.hpp) do (
        "%CF%" -i "%%f"
        if errorlevel 1 (
            echo clang-format failed on %%f
            exit /b 1
        )
    )
)
echo formatted src and include
