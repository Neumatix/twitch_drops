@echo off
:START
echo Closing all open Chrome windows.
taskkill /F /IM chrome.exe /T
if %ERRORLEVEL% neq 0 goto STARTBOT
:STARTBOT
python %~dp0twitch_drops.py
timeout /t 1800
goto START