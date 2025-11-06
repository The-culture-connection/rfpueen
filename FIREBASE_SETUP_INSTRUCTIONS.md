# Firebase Functions Setup Guide

## Quick Setup

You're currently in `~/rfpqueen/rfpueen`. The Firebase Functions need to be set up in your project root.

### Step 1: Navigate to Project Root

```bash
# Go to your project root (where manage.py is)
cd ~/rfpqueen
# or wherever your project root is
```

### Step 2: Create Firebase Functions Directory

```bash
mkdir firebase-functions
cd firebase-functions
```

### Step 3: Initialize Firebase (if not already done)

```bash
# From project root
firebase init functions
```

When prompted:
- Select "Use an existing project" and choose your Firebase project
- Language: JavaScript
- ESLint: Yes (optional)
- Install dependencies: Yes

### Step 4: Copy Function Files

Copy the `index.js` and `package.json` files I created into the `firebase-functions` directory.

### Step 5: Install Dependencies

```bash
cd firebase-functions
npm install
```

### Step 6: Deploy

```bash
# From project root (where firebase.json is)
firebase deploy --only functions
```

## Alternative: Manual Setup

If `firebase init` doesn't work, create these files manually:

1. **firebase.json** (in project root):
```json
{
  "functions": {
    "source": "firebase-functions"
  }
}
```

2. **firebase-functions/package.json** - Already created
3. **firebase-functions/index.js** - Already created

Then:
```bash
cd firebase-functions
npm install
cd ..
firebase deploy --only functions
```

## Troubleshooting

### Error: "Not in a Firebase app directory"
- Make sure `firebase.json` exists in your project root
- Run `firebase deploy` from the directory containing `firebase.json`

### Error: "firebase-functions directory not found"
- Create the directory: `mkdir firebase-functions`
- Copy the function files into it
- Make sure `firebase.json` points to the correct directory

### Error: "Firebase project not found"
- Run `firebase login` first
- Run `firebase use --add` to add your project
- Or set project: `firebase use therfpqueen-f11fd`
