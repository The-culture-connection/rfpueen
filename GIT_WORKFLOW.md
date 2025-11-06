# Git Workflow Guide for RFPueen Project

## ✅ IMPORTANT: Always Work in the Correct Directory

Your Cursor workspace is in: `~/rfpqueen/rfpueen` or `C:\Users\grace\rfpqueen\rfpueen`

**Always use this directory for git commands:**

```bash
cd ~/rfpqueen/rfpueen
```

## Common Git Commands

### Check Status
```bash
cd ~/rfpqueen/rfpueen
git status
```

### Pull Latest Changes
```bash
cd ~/rfpqueen/rfpueen
git pull origin main
```

### Stage Changes
```bash
cd ~/rfpqueen/rfpueen
git add .
```

### Commit Changes
```bash
cd ~/rfpqueen/rfpueen
git commit -m "Your commit message here"
```

### Push to GitHub
```bash
cd ~/rfpqueen/rfpueen
git push origin main
```

### Create a New Branch
```bash
cd ~/rfpqueen/rfpueen
git checkout -b your-branch-name
```

### Push a New Branch
```bash
cd ~/rfpqueen/rfpueen
git push origin your-branch-name
```

## What Was Fixed (Nov 6, 2025)

1. ✅ Aborted the broken rebase in the parent directory
2. ✅ Cleaned up the problematic branch `cursor/develop-fundraising-opportunity-matching-website-ddaa`
3. ✅ Added comprehensive `.gitignore` for Django
4. ✅ Successfully merged and pushed to GitHub main branch
5. ✅ Repository is now clean and up-to-date

## Repository Structure

```
~/rfpqueen/                    ← Parent directory (avoid using for git)
└── rfpueen/                   ← YOUR PROJECT (use this!)
    ├── opportunities/
    ├── rfpueen_project/
    ├── manage.py
    ├── requirements.txt
    └── .gitignore
```

## Notes

- The parent directory (`~/rfpqueen`) also has a git repository, but you should **NOT** use it for development
- Always work from `~/rfpqueen/rfpueen` where your Cursor workspace is located
- The `.gitignore` file now properly excludes Python cache files, logs, environment files, and database files

## Troubleshooting

### If you get "Updates were rejected"
```bash
cd ~/rfpqueen/rfpueen
git pull origin main
# Resolve any conflicts if they occur
git push origin main
```

### If you accidentally work in the wrong directory
Make sure you're in `~/rfpqueen/rfpueen` before running any git commands:
```bash
pwd  # Check current directory
cd ~/rfpqueen/rfpueen  # Navigate to correct directory
```

