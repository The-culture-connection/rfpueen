@echo off
REM Complete Django Setup Script for Windows

echo ==========================================
echo Django RFP Queen - Complete Setup
echo ==========================================
echo.

REM Step 1: Check Python
echo Step 1: Checking Python installation...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    python --version
    set PYTHON_CMD=python
    goto :check_pip
)

py --version >nul 2>&1
if %errorlevel% equ 0 (
    py --version
    set PYTHON_CMD=py
    goto :check_pip
)

echo ERROR: Python not found!
echo Please install Python from https://www.python.org/downloads/
pause
exit /b 1

:check_pip
echo Python found
echo.

REM Step 2: Check pip
echo Step 2: Checking pip...
%PYTHON_CMD% -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo pip not found! Installing...
    %PYTHON_CMD% -m ensurepip --upgrade
)
echo pip found
echo.

REM Step 3: Upgrade pip
echo Step 3: Upgrading pip...
%PYTHON_CMD% -m pip install --upgrade pip --quiet
echo pip upgraded
echo.

REM Step 4: Install Django
echo Step 4: Installing Django...
%PYTHON_CMD% -m pip install Django --quiet
for /f "tokens=*" %%i in ('%PYTHON_CMD% -c "import django; print(django.get_version())"') do set DJANGO_VERSION=%%i
echo Django %DJANGO_VERSION% installed
echo.

REM Step 5: Install dependencies
echo Step 5: Installing project dependencies...
if exist requirements.txt (
    %PYTHON_CMD% -m pip install -r requirements.txt --quiet
    echo Dependencies installed from requirements.txt
) else (
    echo Installing dependencies manually...
    %PYTHON_CMD% -m pip install firebase-admin requests beautifulsoup4 lxml python-dateutil django-cors-headers Pillow --quiet
    echo Dependencies installed
)
echo.

REM Step 6: Check if project exists
echo Step 6: Checking project structure...
if not exist manage.py (
    echo manage.py not found!
    echo Creating Django project...
    
    %PYTHON_CMD% -m django startproject rfpueen_project .
    echo Django project created
    
    %PYTHON_CMD% manage.py startapp opportunities
    echo Opportunities app created
) else (
    echo Project structure found
)
echo.

REM Step 7: Run migrations
echo Step 7: Setting up database...
%PYTHON_CMD% manage.py migrate --noinput
echo Database setup complete
echo.

REM Step 8: Summary
echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo Next steps:
echo 1. Create admin user: %PYTHON_CMD% manage.py createsuperuser
echo 2. Start server: %PYTHON_CMD% manage.py runserver
echo 3. Open browser: http://127.0.0.1:8000/
echo.
echo To stop the server, press Ctrl+C
echo.
pause
