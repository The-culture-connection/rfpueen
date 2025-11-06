# Complete Django Setup Guide for RFP Queen

## Step-by-Step Setup Instructions

### Step 1: Check Python Installation

First, verify Python 3 is installed:

```bash
python3 --version
```

You should see Python 3.8 or higher. If not, install Python 3 first.

### Step 2: Navigate to Project Directory

```bash
cd /workspace
```

### Step 3: Install Dependencies

Install all required Python packages:

```bash
pip3 install -r requirements.txt
```

**Note**: If you get permission errors, use:
```bash
pip3 install --user -r requirements.txt
```

Or better yet, use a virtual environment (recommended):

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Set Up Database

Run migrations to create the database tables:

```bash
python3 manage.py migrate
```

This creates the SQLite database file (`db.sqlite3`) and all necessary tables.

### Step 5: Create Admin User (Optional but Recommended)

Create a superuser account to access the admin panel:

```bash
python3 manage.py createsuperuser
```

Follow the prompts to set username, email, and password.

### Step 6: Start the Django Development Server

Start the server:

```bash
python3 manage.py runserver
```

You should see output like:
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

### Step 7: Access the Application

Open your web browser and go to:

- **Main Dashboard**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/

### To Stop the Server

Press `Ctrl+C` in the terminal where the server is running.

---

## Quick Start (All Commands at Once)

If you want to run everything in sequence:

```bash
cd /workspace
pip3 install -r requirements.txt
python3 manage.py migrate
python3 manage.py createsuperuser  # Follow prompts
python3 manage.py runserver
```

---

## Troubleshooting

### Issue: "No module named 'django'"
**Solution**: Install dependencies: `pip3 install -r requirements.txt`

### Issue: "ModuleNotFoundError"
**Solution**: Make sure you're in the `/workspace` directory and have installed requirements

### Issue: "Port 8000 already in use"
**Solution**: Use a different port:
```bash
python3 manage.py runserver 8080
```

### Issue: "Permission denied"
**Solution**: Use `pip3 install --user -r requirements.txt` or use a virtual environment

### Issue: Can't access from another machine
**Solution**: Run with:
```bash
python3 manage.py runserver 0.0.0.0:8000
```

---

## Next Steps After Setup

1. **Create a user account** via Django admin or registration
2. **Set up your profile** with funding types and interests
3. **Sync opportunities** from Firebase (if configured):
   ```bash
   python3 manage.py sync_opportunities
   ```
4. **Start exploring** opportunities on the explore page

---

## File Structure Overview

```
/workspace/
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
├── db.sqlite3            # Database (created after migrate)
├── rfpueen/              # Main Django project
│   ├── settings.py       # Configuration
│   └── urls.py           # URL routing
├── opportunities/        # Main app
│   ├── models.py         # Database models
│   ├── views.py          # View handlers
│   └── urls.py           # App URLs
└── templates/            # HTML templates
    └── opportunities/
```

---

## Need Help?

- Check Django documentation: https://docs.djangoproject.com/
- Review the README.md file in the project
- Check Django logs in the terminal for error messages
