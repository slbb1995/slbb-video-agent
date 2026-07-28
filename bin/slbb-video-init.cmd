@echo off
setlocal
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
set "SCRIPT_DIR=%~dp0"
where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
  py -3 "%SCRIPT_DIR%slbb-video.py" init %*
) else (
  python "%SCRIPT_DIR%slbb-video.py" init %*
)
exit /b %ERRORLEVEL%
