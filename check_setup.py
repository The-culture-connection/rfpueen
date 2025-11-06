#!/usr/bin/env python3
"""
Setup checker and guide for Django RFP Queen project
"""
import sys
import subprocess
import os

def check_python():
    """Check if Python 3 is installed"""
    print("✓ Checking Python installation...")
    try:
        result = subprocess.run(['python3', '--version'], capture_output=True, text=True)
        print(f"  {result.stdout.strip()}")
        return True
    except FileNotFoundError:
        print("  ✗ Python 3 not found!")
        print("  Please install Python 3.8 or higher")
        return False

def check_django():
    """Check if Django is installed"""
    print("\n✓ Checking Django installation...")
    try:
        result = subprocess.run(['python3', '-c', 'import django; print(django.get_version())'], 
                              capture_output=True, text=True)
        print(f"  Django {result.stdout.strip()} installed")
        return True
    except:
        print("  ✗ Django not installed")
        return False

def install_dependencies():
    """Install dependencies from requirements.txt"""
    print("\n✓ Installing dependencies...")
    if not os.path.exists('requirements.txt'):
        print("  ✗ requirements.txt not found!")
        return False
    
    try:
        result = subprocess.run(['pip3', 'install', '-r', 'requirements.txt'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("  ✓ Dependencies installed successfully")
            return True
        else:
            print(f"  ✗ Error installing dependencies: {result.stderr}")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def run_migrations():
    """Run Django migrations"""
    print("\n✓ Running database migrations...")
    try:
        result = subprocess.run(['python3', 'manage.py', 'migrate'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("  ✓ Migrations completed")
            return True
        else:
            print(f"  ✗ Migration error: {result.stderr}")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def main():
    print("=" * 60)
    print("Django RFP Queen - Setup Checker")
    print("=" * 60)
    
    # Check Python
    if not check_python():
        sys.exit(1)
    
    # Check Django
    django_installed = check_django()
    
    if not django_installed:
        print("\n" + "=" * 60)
        print("Django is not installed. Installing dependencies...")
        print("=" * 60)
        if not install_dependencies():
            print("\n✗ Failed to install dependencies")
            print("\nPlease run manually: pip3 install -r requirements.txt")
            sys.exit(1)
    
    # Run migrations
    if not run_migrations():
        print("\n✗ Failed to run migrations")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✓ Setup Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Create a superuser: python3 manage.py createsuperuser")
    print("2. Start the server: python3 manage.py runserver")
    print("3. Open browser: http://127.0.0.1:8000/")
    print("\n" + "=" * 60)

if __name__ == '__main__':
    main()
