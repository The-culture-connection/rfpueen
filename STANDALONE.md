# Standalone Website - RFP Queen

This is a complete standalone website that can run independently of Squarespace.

## Files Created

1. **index.html** - Main HTML file
2. **styles.css** - Complete CSS styling
3. **app.js** - Main application logic with routing
4. **server.js** - Simple Node.js server (optional)
5. **package.json** - NPM configuration

## Quick Start

### Option 1: Simple HTTP Server (Recommended)

```bash
# Using npm (if you have Node.js installed)
npm install
npm start

# Or using Python
python -m http.server 8080

# Or using PHP
php -S localhost:8080
```

Then open: http://localhost:8080

### Option 2: Node.js Server

```bash
node server.js
```

Then open: http://localhost:3000

### Option 3: Deploy to Static Hosting

Deploy these files to any static hosting service:
- GitHub Pages
- Netlify
- Vercel
- Firebase Hosting
- AWS S3 + CloudFront
- Any web server

## Features

- ✅ Complete standalone website
- ✅ Client-side routing (hash-based)
- ✅ Authentication with Firebase
- ✅ Dashboard, Explore, Applied, Saved pages
- ✅ Responsive design
- ✅ Error handling with visible alerts
- ✅ Modern UI with CSS

## Integration with Squarespace Files

The standalone site uses the same Firebase configuration and logic as the Squarespace files. You can:

1. Use this as a standalone website
2. Extract components for Squarespace
3. Run both in parallel

## Deployment

### Netlify
1. Push to GitHub
2. Connect to Netlify
3. Deploy automatically

### Vercel
```bash
npm i -g vercel
vercel
```

### Firebase Hosting
```bash
npm install -g firebase-tools
firebase init hosting
firebase deploy
```

## Customization

- Edit `styles.css` for styling
- Edit `app.js` for functionality
- Edit `index.html` for structure

## Notes

- The explore page uses a simplified version - full matching logic is in `explore.html`
- All Firebase credentials are the same
- Works with the same Firebase database
