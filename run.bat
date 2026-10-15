@echo off
title GrabSongs
cd /d "%~dp0"
echo Starting GrabSongs...
python app.py %*
