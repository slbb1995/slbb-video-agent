@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
  py -3 "%SCRIPT_DIR%slbb-video.py" ingest %*
) else (
  python "%SCRIPT_DIR%slbb-video.py" ingest %*
)
exit /b %ERRORLEVEL%
