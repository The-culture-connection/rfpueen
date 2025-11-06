#!/bin/bash
# Quick setup script for local machines

echo "=== Django RFP Queen - Local Setup ==="
echo ""

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    PYTHON_CMD="python"
    PIP_CMD="pip"
else
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
fi

echo "Detected Python command: $PYTHON_CMD"
echo ""

# Check Python
if ! command -v $PYTHON_CMD &> /dev/null; then
    echo "ERROR: $PYTHON_CMD not found!"
    echo "Please install Python 3.8 or higher"
    echo ""
    echo "Windows: Download from https://www.python.org/downloads/"
    echo "Mac: brew install python3"
    echo "Linux: sudo apt install python3"
    exit 1
fi

echo "✓ Python found: $($PYTHON_CMD --version)"
echo ""

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "ERROR: manage.py not found!"
    echo "Please navigate to the project directory first"
    echo "Current directory: $(pwd)"
    exit 1
fi

echo "✓ Project directory found"
echo ""

# Install dependencies
echo "Installing dependencies..."
$PIP_CMD install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    echo "Try: $PIP_CMD install --user -r requirements.txt"
    exit 1
fi

echo "✓ Dependencies installed"
echo ""

# Run migrations
echo "Setting up database..."
$PYTHON_CMD manage.py migrate
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to run migrations"
    exit 1
fi

echo "✓ Database setup complete"
echo ""
echo "=== Setup Complete! ==="
echo ""
echo "Next steps:"
echo "1. Create admin user: $PYTHON_CMD manage.py createsuperuser"
echo "2. Start server: $PYTHON_CMD manage.py runserver"
echo "3. Open browser: http://127.0.0.1:8000/"
echo ""
