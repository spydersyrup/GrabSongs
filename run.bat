@echo off
title GrabSongs Music Downloader
cd /d "%~dp0"
echo Starting GrabSongs Music Downloader Service...
python app.py
echo.
echo Process exited with code %ERRORLEVEL%.
pause
