# Quick Setup Commands for Git Bash (Windows)

# Since you're in Git Bash, use these commands:

# 1. Check Python
python3 --version
# or
python --version

# 2. Install Django
pip3 install Django
# or if that doesn't work:
python3 -m pip install Django

# 3. Install all dependencies
pip3 install firebase-admin requests beautifulsoup4 lxml python-dateutil django-cors-headers Pillow
# or if you have requirements.txt:
pip3 install -r requirements.txt

# 4. Check if Django is installed
python3 -m django --version

# 5. Set up database
python3 manage.py migrate

# 6. Create admin user (optional)
python3 manage.py createsuperuser

# 7. Start the server
python3 manage.py runserver

# Then open: http://127.0.0.1:8000/
