@echo off
echo Starting Meat Bro Discord Bot...
echo.

REM Check if virtual environment exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Check if python-dotenv is installed
python -c "import dotenv" 2>nul
if errorlevel 1 (
    echo python-dotenv not found. Installing...
    pip install python-dotenv
)

echo Running bot...
python bot.py

pause
