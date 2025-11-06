# Local Machine Setup Guide

## Troubleshooting Your Errors

### Error 1: `/workspace` directory doesn't exist
**Solution**: You need to navigate to where your project actually is on your computer.

### Error 2: `python3: command not found`
**Solution**: Python might be installed with a different command name.

---

## Step-by-Step Setup for Your Local Machine

### Step 1: Find Your Project Directory

First, find where you cloned/downloaded the project:

**On Windows:**
```cmd
cd C:\path\to\your\project
# or wherever you saved the project
```

**On Mac/Linux:**
```bash
cd ~/path/to/your/project
# or wherever you saved the project
```

**If you're not sure where it is:**
- Look for a folder containing `manage.py` and `requirements.txt`
- Or search for "rfpueen" or "The-culture-connection" folder

### Step 2: Check Python Installation

Try these commands to find Python:

**On Windows:**
```cmd
python --version
# or
py --version
# or
python3 --version
```

**On Mac/Linux:**
```bash
python3 --version
# or
python --version
```

**If Python is not installed:**

**Windows:**
- Download from: https://www.python.org/downloads/
- Make sure to check "Add Python to PATH" during installation

**Mac:**
```bash
# Using Homebrew:
brew install python3

# Or download from: https://www.python.org/downloads/macos/
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip
```

### Step 3: Install Dependencies

Once Python is working, install Django and other packages:

**On Windows:**
```cmd
python -m pip install -r requirements.txt
# or
py -m pip install -r requirements.txt
```

**On Mac/Linux:**
```bash
pip3 install -r requirements.txt
# or
python3 -m pip install -r requirements.txt
```

**If you get permission errors**, use:
```bash
pip3 install --user -r requirements.txt
```

### Step 4: Set Up Database

**On Windows:**
```cmd
python manage.py migrate
# or
py manage.py migrate
```

**On Mac/Linux:**
```bash
python3 manage.py migrate
```

### Step 5: Start the Server

**On Windows:**
```cmd
python manage.py runserver
# or
py manage.py runserver
```

**On Mac/Linux:**
```bash
python3 manage.py runserver
```

Then open: **http://127.0.0.1:8000/** in your browser

---

## Quick Diagnostic Commands

Run these to check your setup:

```bash
# Check current directory
pwd          # Mac/Linux
cd           # Windows

# Check Python
python3 --version   # Mac/Linux
python --version   # Windows/Mac/Linux
py --version       # Windows alternative

# Check if Django is installed
python3 -c "import django; print(django.get_version())"   # Mac/Linux
python -c "import django; print(django.get_version())"   # Windows

# List files in current directory
ls              # Mac/Linux
dir             # Windows
```

---

## Common Issues & Solutions

### Issue: "python3: command not found" (Mac/Linux)
**Solution**: Try `python` instead, or install Python 3:
```bash
# Ubuntu/Debian
sudo apt install python3

# Mac
brew install python3
```

### Issue: "python: command not found" (Windows)
**Solution**: 
- Make sure Python is installed
- Try `py` command instead
- Add Python to PATH during installation

### Issue: "No module named 'django'"
**Solution**: Install dependencies:
```bash
pip3 install -r requirements.txt
# or
python -m pip install -r requirements.txt
```

### Issue: Can't find project files
**Solution**: 
1. Find where you downloaded/cloned the project
2. Navigate there using `cd` command
3. Make sure you see `manage.py` file in that directory

---

## Recommended: Use Virtual Environment

It's best practice to use a virtual environment:

**On Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

**On Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 manage.py migrate
python3 manage.py runserver
```

---

## Need More Help?

1. **Check your operating system**: Windows, Mac, or Linux?
2. **Check Python installation**: Run `python --version` or `python3 --version`
3. **Check project location**: Find the folder with `manage.py`
4. **Share error messages**: Copy the full error output
