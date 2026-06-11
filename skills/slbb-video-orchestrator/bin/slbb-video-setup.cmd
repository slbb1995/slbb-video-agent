@echo off
setlocal
set "SKILL_DIR=%~dp0.."
where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
  py -3 "%SKILL_DIR%\scripts\setup_video_env.py" %*
) else (
  python "%SKILL_DIR%\scripts\setup_video_env.py" %*
)
exit /b %ERRORLEVEL%
