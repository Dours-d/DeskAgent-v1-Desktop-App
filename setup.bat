@echo off
echo Setting up DeskAgent v1...
echo.

REM Create virtual environment
python -m venv venv
call venv\Scripts\activate.bat

REM Install requirements
pip install pandas selenium openpyxl

REM Create directories
mkdir data\.csv 2>nul
mkdir data\chrome_profile 2>nul

echo.
echo Setup complete!
echo.
echo To run DeskAgent:
echo 1. Activate: venv\Scripts\activate.bat
echo 2. Run: python scripts\deskagent_v1.py
echo.
pause