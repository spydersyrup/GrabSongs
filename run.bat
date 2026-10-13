@echo off
title Harmonix Music Downloader
cd /d "%~dp0"
echo ====================================================
echo   Starting Harmonix Music Downloader...
echo ====================================================
python app.py
echo.
echo Process exited with code %ERRORLEVEL%.
pause
