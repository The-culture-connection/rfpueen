#!/bin/bash

# RFPueen Django Server Startup Script

echo "======================================"
echo "Starting RFPueen Server"
echo "======================================"
echo ""

# Check if migrations need to be run
echo "Checking database migrations..."
python3 manage.py makemigrations --check --dry-run

# Check if virtual environment is active
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Warning: No virtual environment detected"
    echo "   Consider using: python3 -m venv venv && source venv/bin/activate"
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found"
    echo "   Copy .env.example to .env and configure Firebase credentials"
    echo "   cp .env.example .env"
fi

echo ""
echo "Starting Django development server..."
echo "Access the application at:"
echo "  - Homepage: http://localhost:8000/"
echo "  - Explore: http://localhost:8000/explore"
echo "  - Dashboard: http://localhost:8000/dashboard"
echo "  - Admin: http://localhost:8000/admin/"
echo "  - API: http://localhost:8000/api/"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 manage.py runserver 0.0.0.0:8000
