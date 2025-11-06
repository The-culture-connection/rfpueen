#!/bin/bash
# Complete Django Setup Script for Mac/Linux

set -e  # Exit on error

echo "=========================================="
echo "Django RFP Queen - Complete Setup"
echo "=========================================="
echo ""

# Step 1: Check Python
echo "Step 1: Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✓ $PYTHON_VERSION found"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version)
    echo "✓ $PYTHON_VERSION found"
    PYTHON_CMD="python"
else
    echo "✗ Python not found!"
    echo "Please install Python 3.8 or higher:"
    echo "  Mac: brew install python3"
    echo "  Linux: sudo apt install python3"
    exit 1
fi

# Step 2: Check pip
echo ""
echo "Step 2: Checking pip..."
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
elif command -v pip &> /dev/null; then
    PIP_CMD="pip"
else
    echo "✗ pip not found! Installing..."
    $PYTHON_CMD -m ensurepip --upgrade
    PIP_CMD="$PYTHON_CMD -m pip"
fi
echo "✓ pip found"

# Step 3: Upgrade pip
echo ""
echo "Step 3: Upgrading pip..."
$PIP_CMD install --upgrade pip --quiet
echo "✓ pip upgraded"

# Step 4: Install Django
echo ""
echo "Step 4: Installing Django..."
$PIP_CMD install Django --quiet
DJANGO_VERSION=$($PYTHON_CMD -c "import django; print(django.get_version())")
echo "✓ Django $DJANGO_VERSION installed"

# Step 5: Install other dependencies
echo ""
echo "Step 5: Installing project dependencies..."
if [ -f "requirements.txt" ]; then
    $PIP_CMD install -r requirements.txt --quiet
    echo "✓ Dependencies installed from requirements.txt"
else
    echo "Installing dependencies manually..."
    $PIP_CMD install firebase-admin requests beautifulsoup4 lxml python-dateutil django-cors-headers Pillow --quiet
    echo "✓ Dependencies installed"
fi

# Step 6: Check if project exists
echo ""
echo "Step 6: Checking project structure..."
if [ ! -f "manage.py" ]; then
    echo "✗ manage.py not found!"
    echo "Creating Django project..."
    
    # Create project
    $PYTHON_CMD -m django startproject rfpueen_project .
    echo "✓ Django project created"
    
    # Create app
    $PYTHON_CMD manage.py startapp opportunities
    echo "✓ Opportunities app created"
else
    echo "✓ Project structure found"
fi

# Step 7: Run migrations
echo ""
echo "Step 7: Setting up database..."
$PYTHON_CMD manage.py migrate --noinput
echo "✓ Database setup complete"

# Step 8: Summary
echo ""
echo "=========================================="
echo "✓ Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Create admin user: $PYTHON_CMD manage.py createsuperuser"
echo "2. Start server: $PYTHON_CMD manage.py runserver"
echo "3. Open browser: http://127.0.0.1:8000/"
echo ""
echo "To stop the server, press Ctrl+C"
echo ""
