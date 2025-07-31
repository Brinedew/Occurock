@echo off
cd /d "%~dp0"
python occurock.py
if errorlevel 1 (
    echo.
    echo Python is required to run Occurock.
    echo Please install Python from https://python.org
    echo.
    pause
)