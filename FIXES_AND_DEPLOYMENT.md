# Fixes and Firebase Functions Setup

## Issues Fixed

### 1. ✅ Logout Functionality
- **Problem**: Templates were using `admin:logout` which requires admin access
- **Fix**: Added proper Django logout view at `/logout/` and updated all templates
- **Files Changed**:
  - `rfpueen/urls.py` - Added logout route
  - All template files - Updated logout links

### 2. ✅ Explore Page
- **Problem**: API calls were using hardcoded URLs that didn't match Django URL patterns
- **Fix**: Updated to use Django URL template tags for proper URL resolution
- **Files Changed**:
  - `templates/opportunities/explore.html` - Fixed API endpoint URLs

### 3. ✅ Applied Page
- **Problem**: Page crashed when opportunity didn't exist in local database
- **Fix**: Added graceful handling for missing opportunities with fallback display
- **Files Changed**:
  - `opportunities/views.py` - Added opportunity existence checking
  - `templates/opportunities/dashboard_applied.html` - Added null checks

### 4. ✅ Firebase Functions Integration
- **Created**: Firebase Functions for optimized computation
- **Functions**:
  - `matchOpportunities` - Handles matching algorithm in Firebase
  - `calculateWinRate` - Calculates win rates in Firebase
- **Benefits**:
  - Reduced Django server load
  - Faster computation
  - Better scalability
  - Automatic fallback to local computation if Functions unavailable

## Firebase Functions Deployment

### Prerequisites
1. Install Firebase CLI:
```bash
npm install -g firebase-tools
```

2. Login to Firebase:
```bash
firebase login
```

3. Navigate to functions directory:
```bash
cd firebase-functions
```

4. Install dependencies:
```bash
npm install
```

### Deploy Functions

Deploy all functions:
```bash
firebase deploy --only functions
```

Or deploy from project root:
```bash
firebase deploy --only functions:matchOpportunities
firebase deploy --only functions:calculateWinRate
```

### After Deployment

1. Update `rfpueen/settings.py` with your actual Firebase Functions URLs:
```python
FIREBASE_FUNCTIONS_BASE_URL = 'https://YOUR-REGION-YOUR-PROJECT.cloudfunctions.net'
```

2. Enable Firebase Functions in settings:
```python
USE_FIREBASE_FUNCTIONS = True  # Set to False to use local computation
```

## Testing

### Test Logout
1. Login to the site
2. Click "Sign out" - should redirect to home page

### Test Explore Page
1. Go to `/explore/`
2. Click "Find Matches"
3. Should display opportunities or show appropriate error message

### Test Applied Page
1. Apply to an opportunity
2. Go to `/dashboard-applied/`
3. Should display applied opportunities without errors

### Test Firebase Functions
1. Set `USE_FIREBASE_FUNCTIONS = True` in settings
2. Try matching opportunities
3. Check Django logs for any Firebase Functions errors
4. If errors occur, it will automatically fallback to local computation

## Configuration

### Enable/Disable Firebase Functions
In `rfpueen/settings.py`:
```python
USE_FIREBASE_FUNCTIONS = True  # Use Firebase Functions
USE_FIREBASE_FUNCTIONS = False # Use local Django computation
```

### Firebase Functions URLs
Update these in `rfpueen/settings.py` after deployment:
```python
FIREBASE_FUNCTIONS_BASE_URL = 'https://us-central1-therfpqueen-f11fd.cloudfunctions.net'
```

## Next Steps

1. **Deploy Firebase Functions**:
   ```bash
   cd firebase-functions
   npm install
   firebase deploy --only functions
   ```

2. **Update Settings**: Update `FIREBASE_FUNCTIONS_BASE_URL` with your actual deployment URL

3. **Test**: Test all functionality to ensure everything works

4. **Monitor**: Check Firebase Functions logs for any issues:
   ```bash
   firebase functions:log
   ```

## Troubleshooting

### If Firebase Functions fail:
- Django automatically falls back to local computation
- Check Firebase Functions logs: `firebase functions:log`
- Verify Firebase project ID matches in settings
- Ensure Firestore collections exist and are accessible

### If explore page doesn't work:
- Check browser console for JavaScript errors
- Verify CSRF token is being sent
- Check Django logs for API errors
- Ensure user is logged in

### If applied page shows errors:
- Check that opportunities exist in database
- Verify applied opportunities have valid opportunity references
- Check Django logs for specific errors
