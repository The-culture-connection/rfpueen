# RFP Queen – Opportunity Matching Platform

This repository hosts a Django application that surfaces the most relevant fundraising opportunities for cultural organizations. It connects to a Firebase Firestore database that stores opportunity listings and user profiles, applies an intelligent matching algorithm, and helps applicants navigate straight to the application pathway.

## Features

- **Intelligent ranking** – matches opportunities using profile focus areas, beneficiaries, geo, funding type, budget fit, and keyword signals. Generates an explainable win-rate prediction with insights and watch-outs.
- **Actionable cards** – swipe-style Apply / Save / Pass controls with real-time feedback and toast notifications. Apply triggers automatic discovery of the direct application URL or creates step-by-step instructions.
- **Pipeline views** – dedicated screens for saved and applied opportunities, synchronized with Firestore collections. Applied records capture application URLs, instructions, and confidence scores.
- **Profile refinement** – Django-managed profile form augments Firebase profile data to refine matching.

## Project structure

```
manage.py
rfpueen/           # Django project configuration
opportunities/     # App with models, views, services, templates
static/            # Compiled CSS/JS assets
templates/         # Global templates (base and auth)
requirements.txt
```

## Getting started

1. **Install dependencies**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Environment configuration**

   Create a `.env` file (or export variables) with:

   ```env
   DJANGO_SECRET_KEY=your-secret
   DJANGO_DEBUG=1
   FIREBASE_PROJECT_ID=therfpqueen-f11fd
   FIREBASE_OPPORTUNITIES_COLLECTION=opportunities
   FIREBASE_PROFILES_COLLECTION=profiles
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/firebase-service-account.json
   ```

   If a filesystem path is unavailable, set `FIREBASE_CREDENTIALS_JSON` with the raw JSON of the service account object.

3. **Database preparation**

   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

4. **Run the development server**

   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

   Visit `http://localhost:8000/` to access the dashboard.

## Firebase integration notes

- Opportunity records should reside in the collection specified by `FIREBASE_OPPORTUNITIES_COLLECTION` and include fields such as `title`, `summary`, `bucket`, `tags`, `funding_amount`, `deadline`, `location`, `eligibility`, `focus_areas`, `beneficiaries`, `funding_type`, `budget_min`, and `budget_max`.
- Profiles belong to `FIREBASE_PROFILES_COLLECTION` and ideally provide `focus_areas`, `target_beneficiaries`, `location`, `organization_type`, `annual_budget_usd`, `keywords`, and `matching_bucket`.
- User interactions are mirrored back to Firestore under `profiles/{uid}/{Applied|Saved|Pass}` with detailed metadata.

## Matching algorithm overview

The score blends weighted criteria (focus alignment, beneficiary overlap, geography, funding type, keywords, organization type, budget fit). Each match surfaces:

- **Score** – normalized between 0 and 1.
- **Win rate** – heuristic percent based on score, clamped between 3% and 99%.
- **Confidence** – reflects data completeness and the share of satisfied criteria.
- **Insights & gaps** – human-readable reasons highlighting matched criteria and any missing data.

## Application pathway discovery

When a user clicks Apply, the system:

1. Attempts to fetch the opportunity URL and crawl for anchor/button elements containing keywords like “apply” or “submit”.
2. Follows likely sub-links up to two levels deep.
3. Returns the direct application URL if discovered, otherwise generates structured instructions and confidence notes.

## Testing

- `python manage.py test` will execute Django tests (add test cases under `opportunities/tests/`).
- For linting, integrate `ruff` or `flake8` as desired.

## Deployment tips

- Set `DJANGO_DEBUG=0` and configure `DJANGO_ALLOWED_HOSTS` in production.
- Use a persistent database (e.g. PostgreSQL) and configure `DATABASE_URL` via `dj-database-url` if needed.
- Serve static files through a CDN or `collectstatic` pipeline.
- Ensure secure storage of Firebase credentials (e.g. Secret Manager / environment variables).
