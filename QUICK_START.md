# 🚀 Quick Start Guide

## Start the Server (3 Steps)

### 1. Configure Firebase (One-time setup)
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your Firebase credentials path
# You need to download the service account JSON from Firebase Console
nano .env
```

### 2. Create Admin User (One-time setup)
```bash
python3 manage.py createsuperuser
# Follow the prompts to create your admin account
```

### 3. Start the Server
```bash
# Option A: Use the startup script
./start_server.sh

# Option B: Run directly
python3 manage.py runserver 0.0.0.0:8000
```

## Access the Application

Open your browser and go to:
- **Homepage**: http://localhost:8000/
- **Explore Opportunities**: http://localhost:8000/explore
- **Dashboard**: http://localhost:8000/dashboard
- **Admin Panel**: http://localhost:8000/admin

## First Time Usage

### 1. Login to Admin
1. Go to http://localhost:8000/admin
2. Login with superuser credentials
3. Create a user account for testing

### 2. Test the API
```bash
# Get API health status
curl http://localhost:8000/api/health/

# Should return: {"status":"ok","message":"RFPueen API is running"}
```

### 3. Sync Opportunities from Firebase (Optional)
```bash
python3 manage.py sync_opportunities --limit 100
```

### 4. Start Exploring
1. Go to http://localhost:8000/explore
2. Select funding types (Contracts, Grants, RFPs, Bids)
3. Enter keywords (e.g., "technology, healthcare")
4. Click "Find Matches"
5. See opportunities with win rates!

## Common Issues

### Issue: Firebase connection error
**Solution**: Make sure your `.env` file has the correct path to your Firebase credentials JSON file.

### Issue: No opportunities showing up
**Solution**: 
1. Check that Firebase has data in the expected collections
2. Try syncing: `python3 manage.py sync_opportunities`

### Issue: Port 8000 already in use
**Solution**: Use a different port:
```bash
python3 manage.py runserver 0.0.0.0:8080
```

## Features to Try

✅ **Smart Matching** - Algorithm ranks opportunities by relevance  
✅ **Win Rate** - See why each opportunity is a good match  
✅ **Apply/Save/Pass** - Manage opportunities with one click  
✅ **Application Finder** - Auto-discovers application form URLs  
✅ **Track Applications** - See all applied opportunities  
✅ **Save for Later** - Bookmark interesting opportunities  

## Getting Help

- **Full Documentation**: See `README.md`
- **Setup Guide**: See `SETUP_GUIDE.md`
- **Project Summary**: See `PROJECT_SUMMARY.md`

## What's Next?

1. **Customize the UI**: Edit templates in `opportunities/templates/`
2. **Adjust Matching**: Modify `opportunities/matching_algorithm.py`
3. **Add Collections**: Update collection map for new data sources
4. **Deploy**: Follow production deployment guide in README.md

That's it! You're ready to match opportunities! 🎉
