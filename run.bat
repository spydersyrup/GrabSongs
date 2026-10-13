@echo off
title Harmonix Downloader
cd /d "%~dp0"
python app.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo An error occurred while launching Harmonix.
    pause
)
