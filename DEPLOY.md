# Deployment Guide - Render (Free Tier)

This guide will help you deploy the Medium Article Scraper to Render's free hosting platform.

## Prerequisites

1. A GitHub account
2. Your code pushed to a GitHub repository
3. A Render account (free signup at https://render.com)

## Step-by-Step Deployment

### Step 1: Prepare Your Code

1. **Initialize Git** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. **Create GitHub Repository**:
   - Go to https://github.com/new
   - Create a new repository (e.g., `medium-scraper`)
   - **DO NOT** initialize with README, .gitignore, or license

3. **Push to GitHub**:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/medium-scraper.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Sign Up for Render

1. Go to https://render.com
2. Click **"Get Started for Free"**
3. Sign up with your GitHub account (recommended)

### Step 3: Create Web Service

1. In Render dashboard, click **"New +"** button
2. Select **"Web Service"**
3. Click **"Connect account"** if prompted
4. Select your GitHub repository (`medium-scraper`)

### Step 4: Configure Service

Fill in the following settings:

- **Name**: `medium-scraper` (or any name you prefer)
- **Environment**: `Python 3`
- **Region**: Choose closest to you (e.g., `Oregon (US West)`)
- **Branch**: `main` (or `master` if that's your branch)
- **Root Directory**: Leave empty (or `./` if needed)
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python app.py`
- **Plan**: Select **Free**

### Step 5: Environment Variables (Optional)

The app will work with default settings. You can optionally add:

- **DEBUG**: `False` (to disable debug mode in production)
- **PORT**: Leave empty (Render sets this automatically)

### Step 6: Deploy

1. Click **"Create Web Service"**
2. Wait for deployment (usually 3-5 minutes)
   - You'll see build logs in real-time
   - First deployment may take longer

### Step 7: Access Your App

Once deployed:
- Your app will be live at: `https://medium-scraper.onrender.com` (or your custom name)
- The URL will be shown in the Render dashboard

### Step 8: Test Your API

Test the API endpoint:
```bash
curl -X POST https://your-app-name.onrender.com/api/search \
  -H "Content-Type: application/json" \
  -d '{"query":"data science"}'
```

Or use PowerShell:
```powershell
$body = @{query='data science'} | ConvertTo-Json
Invoke-RestMethod -Uri 'https://your-app-name.onrender.com/api/search' -Method Post -Body $body -ContentType 'application/json'
```

## Important Notes

### Free Tier Limitations

- **Spinning Down**: Free services spin down after 15 minutes of inactivity
- **First Request**: May take 30-60 seconds to wake up
- **Build Time**: Limited build minutes per month
- **Storage**: CSV file persists, but consider using a database for production

### Troubleshooting

**Build Fails:**
- Check build logs in Render dashboard
- Ensure `requirements.txt` is correct
- Verify Python version in `runtime.txt`

**App Crashes:**
- Check logs in Render dashboard
- Ensure PORT environment variable is used (already configured)
- Verify all dependencies are in `requirements.txt`

**CSV Not Persisting:**
- Free tier has ephemeral storage
- CSV will reset on each deployment
- Consider using Render PostgreSQL (paid) or external storage for production

### Updating Your App

1. Make changes to your code
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Update description"
   git push
   ```
3. Render will automatically redeploy

## Alternative: Railway Deployment

Railway also offers free hosting:

1. Go to https://railway.app
2. Sign up with GitHub
3. Click **"New Project"**
4. Select **"Deploy from GitHub repo"**
5. Choose your repository
6. Railway auto-detects Python and uses `requirements.txt`
7. Set start command: `python app.py`
8. Deploy!

---

**Your app is now live! 🚀**

