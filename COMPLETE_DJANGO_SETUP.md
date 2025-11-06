# Complete Django Setup Guide - Step by Step

## Prerequisites Check

Before starting, make sure you have:
- Python 3.8 or higher installed
- pip (Python package installer)
- Access to terminal/command prompt

---

## Step 1: Install Python (If Not Already Installed)

### Check if Python is installed:

**Windows:**
```cmd
python --version
```
or
```cmd
py --version
```

**Mac/Linux:**
```bash
python3 --version
```

### If Python is NOT installed:

**Windows:**
1. Download from: https://www.python.org/downloads/
2. **IMPORTANT**: Check "Add Python to PATH" during installation
3. Restart your terminal after installation

**Mac:**
```bash
brew install python3
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip
```

---

## Step 2: Navigate to Your Project Directory

Open terminal/command prompt and navigate to where you want the project:

**Windows:**
```cmd
cd C:\Users\YourName\Desktop
# or wherever you want the project
```

**Mac/Linux:**
```bash
cd ~/Desktop
# or wherever you want the project
```

---

## Step 3: Install Django and Dependencies

### Option A: Using pip (Recommended)

**Windows:**
```cmd
python -m pip install --upgrade pip
python -m pip install Django
python -m pip install firebase-admin requests beautifulsoup4 lxml python-dateutil django-cors-headers Pillow
```

**Mac/Linux:**
```bash
pip3 install --upgrade pip
pip3 install Django
pip3 install firebase-admin requests beautifulsoup4 lxml python-dateutil django-cors-headers Pillow
```

### Option B: Using requirements.txt (If you have it)

**Windows:**
```cmd
python -m pip install -r requirements.txt
```

**Mac/Linux:**
```bash
pip3 install -r requirements.txt
```

---

## Step 4: Create Django Project Structure

If you don't have the project files yet, create a new Django project:

**Windows:**
```cmd
django-admin startproject rfpueen_project
cd rfpueen_project
python manage.py startapp opportunities
```

**Mac/Linux:**
```bash
django-admin startproject rfpueen_project
cd rfpueen_project
python3 manage.py startapp opportunities
```

**Note**: If `django-admin` command doesn't work, use:
```bash
python -m django startproject rfpueen_project
```

---

## Step 5: Verify Django Installation

Test that Django is working:

**Windows:**
```cmd
python manage.py --version
```

**Mac/Linux:**
```bash
python3 manage.py --version
```

You should see something like: `5.2.8` or similar version number.

---

## Step 6: Configure Settings

If you're setting up from scratch, you'll need to configure `rfpueen_project/settings.py`:

1. Add 'opportunities' to `INSTALLED_APPS`
2. Configure database settings
3. Set up static files
4. Add Firebase configuration

---

## Step 7: Set Up Database

Run migrations to create database tables:

**Windows:**
```cmd
python manage.py migrate
```

**Mac/Linux:**
```bash
python3 manage.py migrate
```

This creates a `db.sqlite3` file in your project directory.

---

## Step 8: Create Admin User (Optional)

Create a superuser to access the admin panel:

**Windows:**
```cmd
python manage.py createsuperuser
```

**Mac/Linux:**
```bash
python3 manage.py createsuperuser
```

Follow the prompts to set username, email, and password.

---

## Step 9: Start Development Server

**Windows:**
```cmd
python manage.py runserver
```

**Mac/Linux:**
```bash
python3 manage.py runserver
```

You should see:
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

---

## Step 10: Access Your Application

Open your web browser and go to:
- **Main site**: http://127.0.0.1:8000/
- **Admin panel**: http://127.0.0.1:8000/admin/

---

## Troubleshooting

### Error: "django-admin: command not found"
**Solution**: Use `python -m django` instead:
```bash
python -m django startproject rfpueen_project
```

### Error: "No module named 'django'"
**Solution**: Install Django:
```bash
pip3 install Django
# or
python -m pip install Django
```

### Error: "Permission denied"
**Solution**: Use `--user` flag:
```bash
pip3 install --user Django
```

### Error: "Port 8000 already in use"
**Solution**: Use a different port:
```bash
python3 manage.py runserver 8080
```

---

## Quick Reference Commands

```bash
# Check Python version
python3 --version

# Install Django
pip3 install Django

# Create project
django-admin startproject myproject
cd myproject

# Create app
python3 manage.py startapp myapp

# Run migrations
python3 manage.py migrate

# Create superuser
python3 manage.py createsuperuser

# Start server
python3 manage.py runserver

# Stop server
Ctrl+C
```

---

## Next Steps After Setup

1. Copy your project files (models, views, templates) into the Django project
2. Configure settings.py with your app
3. Set up URLs
4. Run migrations for your custom models
5. Start developing!

---

## Need Help?

If you encounter errors:
1. Copy the full error message
2. Check which step you're on
3. Verify Python and Django are installed correctly
4. Make sure you're in the correct directory
