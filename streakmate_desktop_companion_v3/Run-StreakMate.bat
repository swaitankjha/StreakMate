@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  start "" pyw "%~dp0streakmate_desktop.pyw"
) else (
  start "" pythonw "%~dp0streakmate_desktop.pyw"
)
