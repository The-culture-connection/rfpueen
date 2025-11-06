# RFPueen - Opportunity Matching Platform

A Django-based platform for matching opportunities (Contracts, Grants, RFPs, Bids) to user profiles using intelligent algorithms, win rate calculations, and automated application form discovery.

## Features

### 🎯 Smart Opportunity Matching
- **Algorithm-based matching**: Matches opportunities from Firebase based on user's funding types and interests
- **Keyword scoring**: Main interests get 3x weight, sub-interests get 1x weight
- **Collection mapping**: Automatically searches relevant Firebase collections (SAM, grants.gov, PND_RFPs, etc.)

### 📊 Win Rate Calculation with Reasoning
- **Multi-factor analysis**: 
  - Keyword match strength (40 points)
  - Main keyword matches (30 points)
  - Deadline urgency (15 points)
  - Information completeness (15 points)
- **Detailed reasoning**: Provides breakdown and assessment for each opportunity
- **Percentage-based scoring**: Easy-to-understand 0-100% win rate

### 🔍 Application Form Finder
- **Web scraping**: Automatically discovers direct application form URLs
- **Multiple strategies**: 
  - Checks opportunity data for existing URLs
  - Searches for form-related link text
  - Identifies form-related URL patterns
  - Finds form submission actions
  - Detects embedded iframes with forms
- **Caching**: Stores discovered form URLs to avoid repeated scraping
- **Fallback instructions**: Generates helpful instructions when form URL not found

### 💾 Opportunity Management
- **Save for later**: Store interesting opportunities to review and apply later
- **Track applications**: Keep all applied opportunities in one organized place
- **Apply/Pass/Save buttons**: Intuitive card-based UI for quick actions
- **Separate screens**: Dedicated views for applied and saved opportunities

### ⚡ Urgency Tracking
- **Urgent**: Deadlines ≤ 30 days
- **Soon**: Deadlines between 31-92 days  
- **Ongoing**: Deadlines > 92 days or no deadline
- **Color-coded badges**: Visual indicators for quick identification

## Tech Stack

- **Backend**: Django 5.2.8 + Django REST Framework
- **Database**: SQLite (default) / PostgreSQL (recommended for production)
- **Firebase**: Firebase Admin SDK for Firestore integration
- **Web Scraping**: BeautifulSoup4 + Requests + Selenium
- **Frontend**: Vanilla JavaScript + Modern CSS

## Installation

### Prerequisites
- Python 3.12+
- Firebase project with Firestore database
- Firebase service account credentials

### Setup Steps

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd rfpueen
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env and add your Firebase credentials
```

4. **Run database migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Create a superuser**
```bash
python manage.py createsuperuser
```

6. **Run the development server**
```bash
python manage.py runserver
```

7. **Access the application**
- Main site: http://localhost:8000/
- API: http://localhost:8000/api/
- Admin: http://localhost:8000/admin/

## Firebase Setup

### 1. Create Firebase Project
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project or use existing one
3. Enable Firestore Database

### 2. Get Service Account Credentials
1. Go to Project Settings > Service Accounts
2. Click "Generate New Private Key"
3. Download the JSON file
4. Update `FIREBASE_CREDENTIALS_PATH` in `.env` to point to this file

### 3. Firestore Structure
Your Firestore should have these collections for opportunity data:

```
/SAM (Contracts)
/grants.gov (Grants)
/grantwatch (Grants)
/PND_RFPs (RFPs)
/rfpmart (RFPs)
/bid (Bids)

/profiles/{userId}
  /Applied/{opportunityId}
  /Saved/{opportunityId}
```

Each opportunity document should have:
```javascript
{
  "title": "Opportunity Title",
  "description": "Full description",
  "summary": "Brief summary",
  "agency": "Agency Name",
  "department": "Department Name",
  "url": "https://opportunity-url.com",
  "closeDate": "2025-12-31",
  "openDate": "2025-01-01",
  "place": "Location",
  // ... other fields
}
```

## API Endpoints

### Opportunities
- `POST /api/opportunities/match/` - Match opportunities to user profile
- `GET /api/opportunities/{id}/find_application_form/` - Find application form URL

### Applied Opportunities
- `GET /api/applied/` - List all applied opportunities
- `POST /api/applied/` - Mark opportunity as applied
- `DELETE /api/applied/{id}/` - Remove from applied list

### Saved Opportunities
- `GET /api/saved/` - List all saved opportunities
- `POST /api/saved/` - Save opportunity for later
- `POST /api/saved/{id}/apply/` - Move saved to applied
- `DELETE /api/saved/{id}/` - Remove from saved list

### User Profile
- `GET /api/profiles/me/` - Get current user's profile
- `PUT /api/profiles/{id}/` - Update profile

### Dashboard
- `GET /api/dashboard/stats/` - Get dashboard statistics

### Health Check
- `GET /api/health/` - API health check

## Usage

### 1. Finding Opportunities

**Via Web Interface:**
1. Go to `/explore`
2. Select funding types (Contracts, Grants, RFPs, Bids)
3. Enter your main interests (comma-separated keywords)
4. Enter sub-interests (optional)
5. Click "Find Matches"

**Via API:**
```bash
curl -X POST http://localhost:8000/api/opportunities/match/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN" \
  -d '{
    "funding_types": ["Grants", "Contracts"],
    "interests_main": ["technology", "education"],
    "interests_sub": ["software", "training"],
    "exclude_applied": true,
    "exclude_saved": true,
    "limit": 100
  }'
```

### 2. Understanding Win Rate

Each opportunity shows a win rate (0-100%) based on:
- **Keyword Match (40%)**: How many times your keywords appear
- **Main Keywords (30%)**: Number of main interests matched
- **Urgency (15%)**: Deadline timing (sweet spot is "soon")
- **Completeness (15%)**: How complete the opportunity information is

Win rates are categorized as:
- **80%+**: Excellent match - highly recommended
- **60-79%**: Good match - worth pursuing
- **40-59%**: Fair match - consider applying
- **<40%**: Limited match - may not be ideal

### 3. Application Form Finder

The system automatically tries to find direct application form URLs by:
1. Checking opportunity data for existing form URLs
2. Scraping the opportunity page for form-related links
3. Looking for form submission URLs
4. Finding embedded forms in iframes

If no form is found, it generates instructions with:
- Main opportunity URL
- Agency contact information
- Email and phone (if available)
- Deadline information

### 4. Managing Applications

**Save for Later:**
- Click "Save for Later" on any opportunity card
- View saved opportunities at `/dashboard-saved`
- Apply when ready or remove from list

**Track Applications:**
- Click "Apply" to move to applied list
- View all applications at `/dashboard-applied`
- Access application forms directly
- Remove applications as needed

## Matching Algorithm Details

### Collection Mapping
```python
COLLECTION_MAP = {
    "Contracts": ["SAM"],
    "Grants": ["grants.gov", "grantwatch"],
    "RFPs": ["PND_RFPs", "rfpmart"],
    "Bids": ["bid"]
}
```

### Scoring System
```python
# Main keyword match: 3 points per occurrence
# Sub keyword match: 1 point per occurrence
# Total score = sum of all keyword matches

# Example:
# "technology" appears 5 times (main) = 15 points
# "software" appears 3 times (sub) = 3 points
# Total match score = 18 points
```

### Urgency Buckets
```python
days_until_deadline <= 30: "urgent"
days_until_deadline <= 92: "soon"
days_until_deadline > 92: "ongoing"
no deadline: "ongoing"
```

## Deployment

### Development
```bash
python manage.py runserver
```

### Production with Gunicorn
```bash
gunicorn rfpueen_project.wsgi:application --bind 0.0.0.0:8000
```

### Environment Variables for Production
```bash
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
SECRET_KEY=your-production-secret-key
DATABASE_URL=postgresql://...
FIREBASE_CREDENTIALS_PATH=/path/to/credentials.json
```

### Static Files
```bash
python manage.py collectstatic
```

## Project Structure

```
rfpueen/
├── manage.py
├── requirements.txt
├── README.md
├── rfpueen_project/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── opportunities/
    ├── models.py              # Database models
    ├── views.py               # API views
    ├── serializers.py         # REST serializers
    ├── urls.py                # URL routing
    ├── matching_algorithm.py  # Matching logic
    ├── form_scraper.py        # Web scraping
    ├── firebase_service.py    # Firebase integration
    └── templates/             # HTML templates
        ├── base.html
        ├── index.html
        ├── explore.html
        ├── dashboard.html
        ├── dashboard_applied.html
        └── dashboard_saved.html
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Support

For issues, questions, or contributions, please visit the GitHub repository.

## Acknowledgments

- Firebase for the NoSQL database
- Django and Django REST Framework for the backend
- BeautifulSoup4 for web scraping capabilities
