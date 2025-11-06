# RFP Queen - Fundraising Opportunity Matching Platform

An intelligent fundraising opportunity matching platform that connects users with grants, contracts, RFPs, and bids using AI-powered algorithms.

## Features

✨ **Core Functionality:**
- 🎯 **Intelligent Matching Algorithm** - Matches opportunities to user profiles based on keywords, funding types, location, and urgency
- 📊 **Win Rate Calculation** - Calculates success probability (0-100%) with detailed reasoning
- 🔍 **Application Form Discovery** - Automatically finds direct application URLs or provides detailed instructions
- 💾 **Save for Later** - Save opportunities to review and apply later
- 📝 **Application Tracking** - Track all applied opportunities in one place
- 🔥 **Urgency Buckets** - Categorizes opportunities by deadline (urgent, soon, ongoing)

## Tech Stack

- **Backend:** Django 5+ with Django REST Framework
- **Frontend:** HTML/JavaScript with Firebase Authentication
- **Database:** SQLite (development) / PostgreSQL (production recommended)
- **Real-time Data:** Firebase Firestore for opportunity storage
- **Authentication:** Firebase Auth

## Project Structure

```
/workspace/
├── rfpqueen/              # Django project settings
│   ├── settings.py        # Project configuration
│   ├── urls.py           # Main URL routing
│   └── wsgi.py           # WSGI application
├── opportunities/         # Main Django app
│   ├── models.py         # Database models
│   ├── views.py          # API endpoints and HTML views
│   ├── urls.py           # App URL routing
│   ├── admin.py          # Django admin configuration
│   ├── matching.py       # Intelligent matching algorithm
│   ├── firebase_integration.py  # Firebase sync service
│   ├── app_scraper.py    # Application form finder
│   ├── templates/        # HTML templates
│   │   └── opportunities/
│   │       ├── base.html
│   │       ├── index.html      # Dashboard
│   │       ├── explore.html    # Opportunity cards
│   │       ├── applied.html    # Applied opportunities
│   │       └── saved.html      # Saved opportunities
│   └── management/
│       └── commands/
│           └── sync_opportunities.py  # Sync command
├── accounts/             # User authentication app
├── manage.py            # Django management script
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (not in git)
└── README.md           # This file
```

## Installation

### Prerequisites

- Python 3.12+
- pip package manager
- Firebase project with Firestore enabled
- (Optional) Firebase Admin SDK service account key

### Step 1: Clone and Setup

```bash
cd /workspace

# Install dependencies
pip install -r requirements.txt

# Or with system packages
pip install --break-system-packages -r requirements.txt
```

### Step 2: Configure Environment Variables

The `.env` file is already configured with Firebase credentials:

```env
# Firebase Configuration
FIREBASE_API_KEY=AIzaSyDbkrUWV13zBvl4L2lu5Qw5aLYbC9LCjJk
FIREBASE_AUTH_DOMAIN=therfpqueen.firebaseapp.com
FIREBASE_PROJECT_ID=therfpqueen-f11fd

# Django Settings
SECRET_KEY=django-insecure-rfpqueen-development-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,*

# Optional: Firebase Admin SDK (for server-side operations)
# FIREBASE_SERVICE_ACCOUNT_PATH=path/to/serviceAccountKey.json
```

**For Production:** Change `SECRET_KEY`, set `DEBUG=False`, and configure `ALLOWED_HOSTS` appropriately.

### Step 3: Initialize Database

```bash
# Run migrations to create database tables
python manage.py migrate

# Create a superuser for Django admin
python manage.py createsuperuser
```

### Step 4: Sync Opportunities from Firebase

Your existing scraping software populates Firebase with opportunities. Sync them to Django:

```bash
# Sync all opportunities from all collections
python manage.py sync_opportunities

# Sync specific collections
python manage.py sync_opportunities --collections SAM grants.gov

# Limit opportunities per collection (for testing)
python manage.py sync_opportunities --limit 100
```

### Step 5: Run Development Server

```bash
python manage.py runserver 0.0.0.0:8000
```

Visit: `http://localhost:8000`

## API Endpoints

### Authentication
- `POST /api/auth/verify/` - Verify Firebase token and sync user profile

### Opportunities
- `POST /api/match/` - Run matching algorithm for user
- `POST /api/apply/` - Apply to an opportunity
- `POST /api/save/` - Save opportunity for later
- `POST /api/pass/` - Dismiss an opportunity
- `GET /api/applications/` - Get user's applied opportunities
- `GET /api/saved/` - Get user's saved opportunities

### Example API Usage

```javascript
// Verify Firebase user with Django backend
const token = await firebase.auth().currentUser.getIdToken();
const response = await fetch('/api/auth/verify/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ idToken: token })
});
const data = await response.json();

// Run matching algorithm
const matchResponse = await fetch('/api/match/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
        firebase_uid: data.user.firebase_uid 
    })
});
const matches = await matchResponse.json();
```

## Matching Algorithm

The matching algorithm evaluates opportunities based on 5 key factors:

### 1. Keyword Match (40 points)
- Main keywords: 3x weight
- Sub keywords: 1x weight
- Matches in title, description, summary, agency

### 2. Primary Interest Alignment (25 points)
- Number of main interest matches
- Up to 25 points (8 per match)

### 3. Funding Type Match (20 points)
- Matches user's preferred funding types
- Collections mapped to funding types:
  - Contracts → SAM
  - Grants → grants.gov, grantwatch
  - RFPs → PND_RFPs, rfpmart
  - Bids → bid

### 4. Location Match (10 points)
- Same state as user profile

### 5. Timing/Urgency (5 points)
- Urgent (≤30 days): 5 points
- Soon (≤3 months): 3 points
- Ongoing: 2 points

**Win Rate = (Total Score / 100) × 100%**

## Application Form Discovery

The system attempts to find direct application URLs through:

1. **Direct URL fields** in opportunity data (applicationUrl, applyUrl, etc.)
2. **URL pattern matching** in descriptions
3. **Web scraping** of opportunity pages for application links
4. **Keyword scoring** of discovered links

When no direct URL is found, generates detailed application instructions including:
- Main opportunity URL
- Agency contact information
- Email and phone contacts
- Application deadline

## User Profile Fields

Users must complete Firebase profile with:

```javascript
{
  organizationName: "string",
  organizationType: "string",
  city: "string",
  state: "string",
  fundingTypes: ["Grants", "Contracts", "RFPs", "Bids"],
  interestsMain: ["keyword1", "keyword2"],  // Primary interests
  interestsSub: ["keyword3", "keyword4"]    // Secondary interests
}
```

## Django Admin

Access the admin interface at `/admin/` to:
- View and manage opportunities
- Monitor user profiles
- Track applications and saved opportunities
- Review match statistics
- Manage application pathways

## Development Tips

### Running Tests
```bash
python manage.py test opportunities
```

### Database Shell
```bash
python manage.py shell
```

### Clear Database (Reset)
```bash
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

### View Logs
```python
import logging
logger = logging.getLogger(__name__)
logger.info("Your log message")
```

## Production Deployment

### Using Gunicorn

```bash
# Install gunicorn (already in requirements.txt)
pip install gunicorn

# Run production server
gunicorn rfpqueen.wsgi:application --bind 0.0.0.0:8000
```

### Environment Configuration

1. Set `DEBUG=False` in production
2. Configure proper `ALLOWED_HOSTS`
3. Use PostgreSQL instead of SQLite
4. Set up static file serving (whitenoise or nginx)
5. Configure Firebase Admin SDK with service account
6. Enable HTTPS
7. Set strong `SECRET_KEY`

### Database Migration to PostgreSQL

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'rfpqueen_db',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## Monitoring & Maintenance

### Periodic Tasks (Setup with cron or Celery)

1. **Sync Opportunities** - Run daily
   ```bash
   python manage.py sync_opportunities
   ```

2. **Update Match Scores** - Run when new opportunities added
   ```python
   from opportunities.models import UserProfile
   from opportunities.matching import OpportunityMatcher
   
   for profile in UserProfile.objects.all():
       matcher = OpportunityMatcher(profile)
       matcher.match_opportunities()
   ```

3. **Clean Old Opportunities** - Remove expired opportunities
   ```python
   from datetime import datetime, timedelta
   from opportunities.models import Opportunity
   
   cutoff = datetime.now().date() - timedelta(days=90)
   Opportunity.objects.filter(close_date__lt=cutoff).delete()
   ```

## Troubleshooting

### Firebase Connection Issues
- Verify Firebase credentials in `.env`
- Check if Firebase Admin SDK is initialized
- Ensure Firestore database is accessible

### Matching Returns No Results
- Verify user profile has funding types selected
- Check that keywords are set in interests
- Run sync_opportunities to ensure opportunities exist
- Verify collection names match COLLECTION_MAP in matching.py

### Static Files Not Loading
```bash
python manage.py collectstatic
```

## Contributing

This is a custom project for fundraising opportunity matching. For contributions or issues, contact the development team.

## License

Proprietary - All rights reserved

## Support

For questions or issues, please contact the project maintainers.
