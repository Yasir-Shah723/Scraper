# Quick Deployment Guide

## Deploy to Render (Free) - 5 Minutes

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "Ready for deployment"
git remote add origin https://github.com/YOUR_USERNAME/medium-scraper.git
git push -u origin main
```

### 2. Deploy on Render
1. Go to https://render.com → Sign up (free)
2. Click **"New +"** → **"Web Service"**
3. Connect GitHub → Select your repo
4. Settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Plan**: Free
5. Click **"Create Web Service"**
6. Wait 3-5 minutes → Done! 🚀

### 3. Your App URL
After deployment, your app will be at:
```
https://your-app-name.onrender.com
```

### 4. Test API
```bash
curl -X POST https://your-app-name.onrender.com/api/search \
  -H "Content-Type: application/json" \
  -d '{"query":"data science"}'
```

**Note**: Free tier spins down after 15 min inactivity. First request may take 30-60 seconds.

---

See `DEPLOY.md` for detailed instructions.

