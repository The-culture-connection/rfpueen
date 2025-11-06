# RFP Queen - Fundraising Opportunity Matching Website

A Django-based web application that intelligently matches users with fundraising opportunities using advanced algorithms. The system automatically finds application forms and calculates win rates based on match quality.

## Features

- ✅ **Intelligent Matching Algorithm**: Matches opportunities based on user profile, interests, and funding types
- ✅ **Opportunity Cards**: Beautiful card-based UI with Apply, Save, and Pass actions
- ✅ **Application Form Finder**: Automatically scans websites to find direct application forms
- ✅ **Win Rate Calculation**: Calculates success probability with detailed reasoning
- ✅ **Firebase Integration**: Fetches opportunity data from Firebase Firestore
- ✅ **Applied & Saved Tracking**: Separate screens for applied and saved opportunities
- ✅ **Urgency Buckets**: Categorizes opportunities as urgent, soon, or ongoing

## Setup Instructions

### Prerequisites

- Python 3.8+
- Django 4.2+
- Firebase project with Firestore database

### Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up Django:**
```bash
python manage.py migrate
python manage.py createsuperuser
```

### Firebase Setup

**Important**: The Firebase REST API requires authentication. You have two options:

1. **Use Firebase Admin SDK** (Recommended):
   - Download your service account key from Firebase Console
   - Place it in the project root as `serviceAccountKey.json`
   - Update `firebase_client.py` to use the service account

2. **Configure Firestore Rules**:
   - Set your Firestore database to allow read access
   - Or use Firebase REST API with access tokens

For now, the code uses the REST API. If you encounter authentication errors, you'll need to implement one of the above methods.

4. **Run the development server:**
```bash
python manage.py runserver
```

5. **Access the application:**
   - Main dashboard: http://localhost:8000/
   - Admin panel: http://localhost:8000/admin/

## Project Structure

```
rfpueen/
├── rfpueen/              # Django project settings
│   ├── settings.py      # Configuration
│   ├── urls.py          # URL routing
│   └── wsgi.py          # WSGI config
├── opportunities/       # Main app
│   ├── models.py        # Database models
│   ├── views.py         # View handlers
│   ├── urls.py          # App URLs
│   ├── matching.py      # Matching algorithm
│   ├── application_finder.py  # Form finder service
│   └── win_rate.py      # Win rate calculator
├── templates/           # HTML templates
│   └── opportunities/
├── static/             # Static files
└── manage.py           # Django management script
```

## Key Components

### Matching Algorithm (`opportunities/matching.py`)

- Calculates relevance scores based on keyword matches
- Filters by funding types and collections
- Sorts by match quality
- Considers urgency buckets

### Application Form Finder (`opportunities/application_finder.py`)

- Scans opportunity websites for application forms
- Looks for form elements, links, and buttons
- Generates instructions when forms aren't found
- Uses BeautifulSoup for HTML parsing

### Win Rate Calculator (`opportunities/win_rate.py`)

- Calculates success probability (0-100%)
- Considers keyword matches, urgency, form availability
- Provides detailed reasoning for each calculation

## API Endpoints

- `POST /api/match/` - Find matching opportunities
- `POST /api/apply/<opp_id>/` - Apply to an opportunity
- `POST /api/save/<opp_id>/` - Save an opportunity
- `POST /api/pass/<opp_id>/` - Pass on an opportunity
- `POST /api/remove-applied/<opp_id>/` - Remove from applied list
- `POST /api/remove-saved/<opp_id>/` - Remove from saved list
- `POST /api/find-application-form/` - Find application form for an opportunity

## Database Models

- **UserProfile**: User preferences and interests
- **Opportunity**: Opportunity data from Firebase
- **AppliedOpportunity**: User's applied opportunities with win rates
- **SavedOpportunity**: User's saved opportunities

## Configuration

### Firebase Collections Mapping

The system maps funding types to Firebase collections:

- **Contracts** → `SAM`
- **Grants** → `grants.gov`, `grantwatch`
- **RFPs** → `PND_RFPs`, `rfpmart`
- **Bids** → `bid`

Update `COLLECTION_MAP` in `settings.py` to customize.

## Usage

1. **Create a user account** via Django admin or registration
2. **Set up your profile** with funding types and interests
3. **Explore opportunities** - Click "Find Matches" to see matched opportunities
4. **Apply or Save** - Use the action buttons on each opportunity card
5. **View Applied/Saved** - Check separate screens for your tracked opportunities

## Development Notes

- The application uses Django's built-in authentication
- Firebase integration uses REST API (no admin SDK required)
- Application form finder may take a few seconds per URL
- Win rate calculations are performed server-side

## License

This project is part of The Culture Connection organization.
