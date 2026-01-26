@echo off
REM install.bat
echo Setting up DeskAgent v1...

REM Create virtual environment
python -m venv venv
call venv\Scripts\activate.bat

REM Install requirements
pip install -r scripts\requirements.txt

REM Create necessary directories
mkdir data\.csv 2>nul
mkdir data\backups 2>nul
mkdir data\exports 2>nul

echo.
echo Installation complete!
echo.
echo To run DeskAgent:
echo 1. Activate virtual environment: venv\Scripts\activate.bat
echo 2. Run: python scripts\deskagent_v1.py
echo.
pause