@echo off
setlocal

@REM Get the absolute directory path of the current batch file
set BASEDIR=%~dp0
set BASEDIR=%BASEDIR:~0,-1%
set PROJDIR=%BASEDIR%\..
cd %PROJDIR%

REM Kill previous instance of this bat file
taskkill /F /FI "WindowTitle eq Melon Music Player" /T>nul

REM Title the instance so it can be identified later
TITLE Melon Music Player
".venv\Scripts\python.exe" -m mpserver.main

endlocal