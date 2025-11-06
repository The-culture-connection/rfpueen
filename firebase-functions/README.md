# Firebase Functions Setup

## Installation

1. Install Firebase CLI:
```bash
npm install -g firebase-tools
```

2. Login to Firebase:
```bash
firebase login
```

3. Initialize Firebase Functions (if not already done):
```bash
cd firebase-functions
npm install
```

## Deployment

Deploy all functions:
```bash
firebase deploy --only functions
```

Deploy specific function:
```bash
firebase deploy --only functions:matchOpportunities
```

## Functions

- `matchOpportunities`: Matches opportunities based on user profile
- `calculateWinRate`: Calculates win rate for a specific opportunity

## Usage

After deployment, functions will be available at:
- `https://us-central1-therfpqueen-f11fd.cloudfunctions.net/matchOpportunities`
- `https://us-central1-therfpqueen-f11fd.cloudfunctions.net/calculateWinRate`

Update Django settings to use these URLs.
