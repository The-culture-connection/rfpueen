# RFP Queen - Deployment Guide

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt --break-system-packages

# 2. Configure environment variables (already done in .env)
# Edit .env if needed

# 3. Run migrations
python manage.py migrate

# 4. Create admin user
python manage.py createsuperuser

# 5. Sync opportunities from Firebase
python manage.py sync_opportunities --limit 100

# 6. Start development server
python manage.py runserver 0.0.0.0:8000
```

## Accessing the Application

- **Main Dashboard:** http://localhost:8000/
- **Explore Opportunities:** http://localhost:8000/explore/
- **Applied Opportunities:** http://localhost:8000/applied/
- **Saved Opportunities:** http://localhost:8000/saved/
- **Django Admin:** http://localhost:8000/admin/

## User Workflow

1. **Sign In** - Users sign in with Firebase Authentication (email/password)
2. **Profile Sync** - System syncs user profile from Firebase (funding types, interests)
3. **Explore** - Click "Find Matches" to run intelligent matching algorithm
4. **Review Cards** - Opportunities displayed with win rate and urgency
5. **Take Action:**
   - **Apply** - System finds application form or provides instructions
   - **Save** - Save for later review
   - **Pass** - Dismiss opportunity
6. **Track** - View applied and saved opportunities in separate screens

## Firebase Setup

Your existing Firebase project is configured:
- **Project ID:** therfpqueen-f11fd
- **Auth Domain:** therfpqueen.firebaseapp.com

### User Profile Structure in Firebase

Users must have profiles in `profiles/{uid}` with:

```javascript
{
  organizationName: "Organization Name",
  organizationType: "Nonprofit",  // or "Government", "Business", etc.
  city: "City Name",
  state: "State Name",
  fundingTypes: ["Grants", "Contracts"],  // Options: Grants, Contracts, RFPs, Bids
  interestsMain: ["education", "healthcare"],  // Primary keywords
  interestsSub: ["technology", "community"]    // Secondary keywords
}
```

### Opportunity Collections in Firebase

The system expects opportunities in these collections:
- `SAM` - Federal contracts
- `grants.gov` - Federal grants
- `grantwatch` - Grant opportunities
- `PND_RFPs` - RFP listings
- `rfpmart` - RFP marketplace
- `bid` - Bid opportunities

### Opportunity Data Structure

```javascript
{
  title: "Opportunity Title",
  description: "Full description",
  summary: "Brief summary",
  agency: "Agency Name",
  department: "Department Name",
  openDate: "2025-01-01",  // or postedDate
  closeDate: "2025-12-31",  // or deadline
  city: "City",
  state: "State",
  place: "Full Location",
  url: "https://...",  // Main URL
  synopsisUrl: "https://...",  // Alternative URL
  link: "https://...",  // Alternative URL
  contactEmail: "contact@example.com",
  contactPhone: "+1-555-0100"
}
```

## Production Deployment

### 1. Environment Variables

Update `.env` for production:

```env
SECRET_KEY=<generate-strong-key>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Firebase Admin SDK (recommended for production)
FIREBASE_SERVICE_ACCOUNT_PATH=/path/to/serviceAccountKey.json
```

### 2. Database

Switch to PostgreSQL:

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'rfpqueen_db',
        'USER': 'postgres_user',
        'PASSWORD': 'secure_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 3. Static Files

```bash
# Collect static files
python manage.py collectstatic

# Configure static files serving (whitenoise or nginx)
```

### 4. Gunicorn + Nginx

```bash
# Start with Gunicorn
gunicorn rfpqueen.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

Nginx configuration:

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /path/to/staticfiles/;
    }
}
```

### 5. Systemd Service

Create `/etc/systemd/system/rfpqueen.service`:

```ini
[Unit]
Description=RFP Queen Django Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/workspace
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/gunicorn --workers 3 --bind 0.0.0.0:8000 rfpqueen.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable rfpqueen
sudo systemctl start rfpqueen
```

## Automated Tasks

### Cron Jobs

Add to crontab (`crontab -e`):

```bash
# Sync opportunities daily at 2 AM
0 2 * * * cd /workspace && python manage.py sync_opportunities >> /var/log/rfpqueen_sync.log 2>&1

# Clean old opportunities weekly
0 3 * * 0 cd /workspace && python manage.py shell < cleanup_script.py
```

### Cleanup Script

Create `cleanup_script.py`:

```python
from datetime import datetime, timedelta
from opportunities.models import Opportunity

# Remove opportunities older than 90 days past deadline
cutoff = datetime.now().date() - timedelta(days=90)
deleted_count = Opportunity.objects.filter(close_date__lt=cutoff).delete()
print(f"Deleted {deleted_count[0]} old opportunities")
```

## Monitoring

### Health Check Endpoint

Add to `opportunities/views.py`:

```python
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({'status': 'healthy'})
```

### Logging

Configure in `settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/rfpqueen/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
        'opportunities': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

## Security Checklist

- [ ] Set strong SECRET_KEY
- [ ] Set DEBUG=False in production
- [ ] Configure proper ALLOWED_HOSTS
- [ ] Enable HTTPS/SSL
- [ ] Set secure cookie flags
- [ ] Configure CORS properly
- [ ] Use environment variables for sensitive data
- [ ] Enable Django security middleware
- [ ] Set up firewall rules
- [ ] Regular security updates

## Performance Optimization

1. **Database Indexing** - Already configured in models
2. **Query Optimization** - Use select_related() and prefetch_related()
3. **Caching** - Add Redis/Memcached for frequent queries
4. **CDN** - Serve static files from CDN
5. **Database Connection Pooling** - Use pgbouncer for PostgreSQL

## Troubleshooting

### Issue: No opportunities found
**Solution:** Run `python manage.py sync_opportunities`

### Issue: Matching returns no results
**Solution:** Verify user profile has funding types and interests set in Firebase

### Issue: Firebase connection error
**Solution:** Check Firebase credentials in `.env` and ensure Firestore is accessible

### Issue: Static files not loading
**Solution:** Run `python manage.py collectstatic` and configure static file serving

## Support

For issues or questions, refer to the main README.md or contact the development team.
