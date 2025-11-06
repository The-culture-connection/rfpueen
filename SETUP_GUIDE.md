# Quick Setup Guide for RFPueen

## Step-by-Step Setup

### 1. Install Dependencies (Already Done)
```bash
pip3 install -r requirements.txt
```

### 2. Configure Firebase

You need to set up Firebase credentials. You have two options:

#### Option A: Using Service Account JSON File (Recommended)
1. Go to Firebase Console: https://console.firebase.google.com/
2. Select your project: `therfpqueen-f11fd`
3. Go to Project Settings > Service Accounts
4. Click "Generate New Private Key"
5. Download the JSON file
6. Save it somewhere secure (e.g., `/workspace/firebase-credentials.json`)
7. Create `.env` file:
```bash
cp .env.example .env
```
8. Edit `.env` and set:
```
FIREBASE_CREDENTIALS_PATH=/workspace/firebase-credentials.json
```

#### Option B: Use Existing Firebase Config
Since you already have Firebase configuration in your HTML files, you can add this to your Django settings.

Edit `/workspace/rfpueen_project/settings.py` and uncomment the FIREBASE_CONFIG section:

```python
FIREBASE_CONFIG = {
    "type": "service_account",
    "project_id": "therfpqueen-f11fd",
    # Add other required fields from your service account JSON
}
```

### 3. Run the Server

```bash
cd /workspace
python3 manage.py runserver 0.0.0.0:8000
```

### 4. Create Admin User

In a new terminal:
```bash
cd /workspace
python3 manage.py createsuperuser
```

Follow the prompts to create your admin account.

### 5. Access the Application

- **Homepage**: http://localhost:8000/
- **Explore Opportunities**: http://localhost:8000/explore
- **Dashboard**: http://localhost:8000/dashboard
- **Applied Opportunities**: http://localhost:8000/dashboard-applied
- **Saved Opportunities**: http://localhost:8000/dashboard-saved
- **Admin Panel**: http://localhost:8000/admin
- **API Root**: http://localhost:8000/api/
- **API Health Check**: http://localhost:8000/api/health/

## Testing the API

### 1. Get Authentication Token

First, create a user via the admin panel or use Django's shell:

```bash
python3 manage.py shell
```

Then:
```python
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

user = User.objects.create_user('testuser', 'test@example.com', 'password123')
token = Token.objects.create(user=user)
print(f"Token: {token.key}")
```

### 2. Test API Endpoints

#### Health Check
```bash
curl http://localhost:8000/api/health/
```

#### Match Opportunities
```bash
curl -X POST http://localhost:8000/api/opportunities/match/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -d '{
    "funding_types": ["Grants", "Contracts"],
    "interests_main": ["technology", "education"],
    "interests_sub": ["software", "training"],
    "limit": 50
  }'
```

#### Get Dashboard Stats
```bash
curl http://localhost:8000/api/dashboard/stats/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

## Troubleshooting

### Firebase Connection Issues

If you get Firebase errors:

1. Make sure your Firebase credentials are correct
2. Check that the path in `.env` is absolute and correct
3. Verify your Firebase project has Firestore enabled
4. Make sure you have the correct permissions

### Database Issues

If you need to reset the database:

```bash
rm db.sqlite3
rm -rf opportunities/migrations/0*.py
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py createsuperuser
```

### Port Already in Use

If port 8000 is busy:

```bash
python3 manage.py runserver 0.0.0.0:8080
```

Then access at http://localhost:8080/

## Features to Test

1. **Matching Algorithm**
   - Go to /explore
   - Select funding types
   - Add keywords
   - Click "Find Matches"
   - You should see opportunities ranked by match score and win rate

2. **Win Rate Calculation**
   - Each opportunity card shows win rate percentage
   - Hover or click to see detailed reasoning

3. **Application Form Finder**
   - The system tries to find direct application URLs
   - If found, shows "Apply" button with direct link
   - If not found, provides instructions

4. **Save & Apply**
   - Click "Save for Later" to save an opportunity
   - Go to /dashboard-saved to see saved items
   - Click "Apply Now" to move to applied list
   - Go to /dashboard-applied to see applications

5. **Pass/Remove**
   - Click "Pass" to skip an opportunity
   - Click "Remove" to delete from saved/applied lists

## Next Steps

1. **Add Your Firebase Data**
   - Make sure your Firebase Firestore has opportunity data in the expected collections
   - Collection names: SAM, grants.gov, grantwatch, PND_RFPs, rfpmart, bid

2. **Customize Matching**
   - Edit `/workspace/opportunities/matching_algorithm.py` to adjust scoring
   - Modify weights for main vs sub keywords
   - Change urgency bucket thresholds

3. **Enhance UI**
   - Templates are in `/workspace/opportunities/templates/`
   - Add your branding, colors, logos

4. **Production Deployment**
   - Use PostgreSQL instead of SQLite
   - Set DEBUG=False in settings
   - Configure proper SECRET_KEY
   - Set up gunicorn with nginx
   - Use environment variables for all secrets

## API Documentation

Full API documentation is available in the README.md file.

Key endpoints:
- `POST /api/opportunities/match/` - Match opportunities
- `GET /api/applied/` - List applied
- `POST /api/applied/` - Mark as applied
- `GET /api/saved/` - List saved
- `POST /api/saved/` - Save for later
- `GET /api/dashboard/stats/` - Dashboard stats

## Support

For issues or questions, check the README.md file or the Django documentation.
