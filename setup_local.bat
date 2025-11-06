@echo off
REM Quick setup script for Windows

echo === Django RFP Queen - Local Setup ===
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python found
python --version
echo.

REM Check if we're in the right directory
if not exist manage.py (
    echo ERROR: manage.py not found!
    echo Please navigate to the project directory first
    echo Current directory: %CD%
    pause
    exit /b 1
)

echo Project directory found
echo.

REM Install dependencies
echo Installing dependencies...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo Dependencies installed
echo.

REM Run migrations
echo Setting up database...
python manage.py migrate
if %errorlevel% neq 0 (
    echo ERROR: Failed to run migrations
    pause
    exit /b 1
)

echo Database setup complete
echo.
echo === Setup Complete! ===
echo.
echo Next steps:
echo 1. Create admin user: python manage.py createsuperuser
echo 2. Start server: python manage.py runserver
echo 3. Open browser: http://127.0.0.1:8000/
echo.
pause
