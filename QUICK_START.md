# Quick Start Guide - RFP Queen

## 🚀 Get Started in 5 Minutes

### Step 1: Start the Server

```bash
cd /workspace
python3 manage.py runserver 0.0.0.0:8000
```

### Step 2: Access the Application

Open your browser to: **http://localhost:8000**

### Step 3: Sign In

Use your Firebase email/password credentials.

If you don't have an account, create one in Firebase Console first.

### Step 4: Sync Opportunities

In a new terminal:

```bash
cd /workspace
python3 manage.py sync_opportunities --limit 50
```

This syncs 50 opportunities per collection from Firebase to Django.

### Step 5: Find Matches

1. Go to **http://localhost:8000/explore/**
2. Click **"Find Matches"** button
3. Review opportunity cards with win rates
4. Click **Apply**, **Save**, or **Pass** on each card

### Step 6: Track Applications

- **Applied:** http://localhost:8000/applied/
- **Saved:** http://localhost:8000/saved/
- **Dashboard:** http://localhost:8000/

## 🎯 What Each Feature Does

### Dashboard (/)
- Overview of your activity
- Counts of applied and saved opportunities
- Quick links to Explore, Applied, Saved

### Explore (/explore/)
- **Find Matches** button runs the matching algorithm
- Shows opportunities ranked by relevance
- **Win Rate %** indicates match quality
- **Urgency badge** shows deadline status:
  - 🔴 Urgent: ≤30 days
  - 🟡 Soon: ≤3 months  
  - ⚪ Ongoing: >3 months
- **Three buttons** for each opportunity:
  - **Apply** - Finds application form or shows instructions
  - **Save** - Stores for later review
  - **Pass** - Dismisses from list

### Applied (/applied/)
- List of all opportunities you've applied to
- Shows application date and deadline
- Links to application forms (if found)
- Links to full opportunity details

### Saved (/saved/)
- Opportunities you saved for later
- Can apply directly from this page
- Shows when you saved each opportunity

## 📊 Understanding Win Rates

Win rates are calculated based on:

- **40%** - How many of your keywords appear in the opportunity
- **25%** - Match with your primary interests
- **20%** - Funding type preference match
- **10%** - Location match (same state)
- **5%** - Deadline timing

**Example:**
- 90%+ = Excellent match, highly recommended
- 70-89% = Good match, worth applying
- 50-69% = Fair match, review carefully
- <50% = Weak match, probably not a fit

## 🔧 Common Commands

### Sync all opportunities
```bash
python3 manage.py sync_opportunities
```

### Sync specific collections
```bash
python3 manage.py sync_opportunities --collections SAM grants.gov
```

### Sync limited number (testing)
```bash
python3 manage.py sync_opportunities --limit 10
```

### Access Django Admin
1. Create superuser (first time only):
   ```bash
   python3 manage.py createsuperuser
   ```

2. Visit: http://localhost:8000/admin/

### Reset database (start fresh)
```bash
rm db.sqlite3
python3 manage.py migrate
python3 manage.py createsuperuser
python3 manage.py sync_opportunities
```

## 🐛 Troubleshooting

### "No matches found"
- **Check:** User profile in Firebase has funding types and interests set
- **Fix:** Add to Firebase: `fundingTypes`, `interestsMain`, `interestsSub`
- **Verify:** Run sync_opportunities to ensure opportunities exist

### "Firebase connection error"
- **Check:** `.env` file has correct Firebase credentials
- **Fix:** Verify API key, auth domain, project ID

### "Module not found" errors
- **Fix:** Install requirements:
  ```bash
  pip3 install -r requirements.txt --break-system-packages
  ```

### Port 8000 already in use
- **Fix:** Use different port:
  ```bash
  python3 manage.py runserver 0.0.0.0:8080
  ```

### No opportunities in database
- **Check:** Run sync command first
- **Verify:** Your scraping software has populated Firebase collections

## 📁 Required Firebase Profile Structure

Users MUST have this data in `profiles/{uid}`:

```javascript
{
  organizationName: "Your Organization",
  organizationType: "Nonprofit",  // or "Government", "Business", etc.
  city: "Your City",
  state: "Your State",
  
  // REQUIRED FOR MATCHING:
  fundingTypes: [
    "Grants",      // and/or
    "Contracts",   // and/or
    "RFPs",        // and/or
    "Bids"
  ],
  
  // REQUIRED FOR MATCHING:
  interestsMain: [
    "education",
    "healthcare",
    "technology"
  ],
  
  // REQUIRED FOR MATCHING:
  interestsSub: [
    "rural communities",
    "youth programs",
    "research"
  ]
}
```

Without these fields, matching will return zero results!

## 🎓 Example User Flow

**Sarah's Story:**

1. **Signs in** with her email (sarah@nonprofit.org)
2. **Profile checked:** She has:
   - Funding Types: ["Grants", "RFPs"]
   - Main Interests: ["education", "community development"]
   - Sub Interests: ["literacy", "after-school programs"]
   - State: "California"

3. **Clicks "Find Matches"**:
   - System searches SAM, grants.gov, grantwatch, PND_RFPs, rfpmart
   - Finds 47 opportunities with matching keywords
   - Calculates win rates for each
   - Shows top 20, sorted by relevance

4. **Reviews first opportunity**:
   - Title: "After-School Literacy Program Grant"
   - Win Rate: 92%
   - Urgency: Urgent (15 days left)
   - Clicks **"Apply"**

5. **System response**:
   - Scrapes opportunity page
   - Finds: grants.gov/apply/form-12345
   - Opens application in new tab
   - Moves opportunity to "Applied" list

6. **Reviews second opportunity**:
   - Win Rate: 65%
   - Deadline: 3 months away
   - Clicks **"Save for Later"**
   - Moves to "Saved" list

7. **Later that week**:
   - Visits /saved/
   - Reviews saved opportunity
   - Clicks "Apply Now"
   - Gets detailed instructions

## 💡 Pro Tips

1. **Be specific with interests** - "early childhood education" > "education"
2. **Review win rates** - Focus on 70%+ matches
3. **Act on urgent** - Red badges mean apply ASAP
4. **Use save feature** - Don't lose good opportunities
5. **Check applied tab** - Track your submissions
6. **Sync regularly** - New opportunities added daily

## 🚦 System Status Indicators

On opportunity cards:

- **Collection Badge** (gray) - Data source (SAM, grants.gov, etc.)
- **Urgency Badge**:
  - 🔴 RED = Apply now! (≤30 days)
  - 🟡 YELLOW = Apply soon (≤3 months)
  - ⚪ GRAY = No rush (ongoing)
- **Win Rate Badge** (purple) - Match quality percentage

## 📞 Need Help?

1. Check README.md for full documentation
2. Check DEPLOYMENT.md for setup details
3. Check PROJECT_SUMMARY.md for technical details
4. View Django admin for data inspection
5. Check server logs for errors

---

**You're all set! Start finding and applying to opportunities! 🎉**
