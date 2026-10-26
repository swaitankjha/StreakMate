@echo off
setlocal
set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "TARGET=%STARTUP%\StreakMate.bat"
set "SOURCE=%~dp0Run-StreakMate.bat"
(
  echo @echo off
  echo start "" "%SOURCE%"
) > "%TARGET%"
echo StreakMate will start when you sign in to Windows.
echo To undo this, delete:
echo %TARGET%
pause
