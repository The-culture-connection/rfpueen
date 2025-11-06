# Firebase Functions Setup - Step by Step

## The Problem
You're getting "No such file or directory" because the `firebase-functions` folder doesn't exist in your local repository yet.

## Solution: Set Up Firebase Functions

### Step 1: Navigate to Your Project Root

You're currently in `~/rfpqueen/rfpueen`. Go to the project root:

```bash
cd ~/rfpqueen
# Make sure you're where manage.py is located
```

### Step 2: Initialize Firebase (Recommended)

```bash
firebase init functions
```

When prompted:
- **Select**: "Use an existing project"
- **Choose**: `therfpqueen-f11fd` (your Firebase project)
- **Language**: JavaScript
- **ESLint**: Yes (or No if you prefer)
- **Install dependencies**: Yes

This will create the `firebase-functions` directory and `firebase.json`.

### Step 3: Copy Function Files

After initialization, copy the function code:

1. Copy `firebase-functions/index.js` content (already created in workspace)
2. Copy `firebase-functions/package.json` content (already created)

Or manually create these files:

**Create `firebase-functions/index.js`** with the Firebase Functions code

**Create `firebase-functions/package.json`**:
```json
{
  "name": "rfpqueen-functions",
  "version": "1.0.0",
  "description": "Firebase Functions for RFP Queen",
  "main": "index.js",
  "scripts": {
    "serve": "firebase emulators:start --only functions",
    "shell": "firebase functions:shell",
    "start": "npm run shell",
    "deploy": "firebase deploy --only functions",
    "logs": "firebase functions:log"
  },
  "engines": {
    "node": "18"
  },
  "dependencies": {
    "firebase-admin": "^11.0.0",
    "firebase-functions": "^4.0.0"
  },
  "devDependencies": {
    "firebase-functions-test": "^3.0.0"
  },
  "private": true
}
```

### Step 4: Install Dependencies

```bash
cd firebase-functions
npm install
```

### Step 5: Deploy

```bash
# Go back to project root
cd ..

# Deploy functions
firebase deploy --only functions
```

## Alternative: Manual Setup (If firebase init doesn't work)

### 1. Create firebase.json in project root:

```json
{
  "functions": {
    "source": "firebase-functions"
  }
}
```

### 2. Create firebase-functions directory:

```bash
mkdir firebase-functions
cd firebase-functions
```

### 3. Create package.json and index.js files

### 4. Install and deploy:

```bash
npm install
cd ..
firebase deploy --only functions
```

## Quick Commands Summary

```bash
# 1. Go to project root
cd ~/rfpqueen

# 2. Initialize Firebase (or create manually)
firebase init functions

# 3. Install dependencies
cd firebase-functions
npm install

# 4. Deploy
cd ..
firebase deploy --only functions
```

## Verify Setup

After deployment, you should see:
```
✔  functions[matchOpportunities(us-central1)] Successful create operation.
✔  functions[calculateWinRate(us-central1)] Successful create operation.
```

Then update your Django settings with the function URLs!
