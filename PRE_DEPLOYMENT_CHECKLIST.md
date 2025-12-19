# 🚀 Render Deployment - Quick Start Checklist

## Before You Deploy - Verify These Files

Run this checklist to ensure everything is ready for Render deployment:

### ✅ Step 1: Check Required Files

```bash
# In your FMF folder, verify these files exist:

# 1. API Service
ls app/server/api_services.py

# 2. Web Interface  
ls app/web/index.html

# 3. Database Connector
ls app/dbconnector.py

# 4. Database Files
ls DB/1_ImageDB.sqlite
ls DB/1_faiss_face_index.bin
ls DB/1_face_metadata.pkl

# 5. Images Folder
ls Images/

# 6. Deployment Files
ls Procfile
ls requirements.txt
ls render.yaml
ls runtime.txt
```

### ✅ Step 2: Git Commit & Push

```bash
# Add all files to git
git add .

# Commit
git commit -m "Ready for Render deployment"

# Push to GitHub
git push origin master
```

### ✅ Step 3: Environment Variables to Set in Render

When creating your web service, add these environment variables:

```
DB_FOLDER=/opt/render/project/src/DB
IMAGE_FOLDER=/opt/render/project/src/Images
PYTHON_VERSION=3.11.9
```

### ✅ Step 4: Render Configuration

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
uvicorn app.server.api_services:service --host 0.0.0.0 --port $PORT
```

### ✅ Step 5: After First Deployment

Once your app is live at `https://your-app.onrender.com`, update the API URL:

1. Open `app/web/index.html`
2. Find line 562:
   ```javascript
   const API_BASE = 'http://localhost:8000';
   ```
3. Change to:
   ```javascript
   const API_BASE = 'https://your-app.onrender.com';
   ```
4. Commit and push again

### 📝 Quick Commands

```bash
# Check if all required files are present
ls app/server/api_services.py app/web/index.html app/dbconnector.py DB/*.sqlite DB/*.bin DB/*.pkl

# View current git status
git status

# Add and commit all changes
git add . && git commit -m "Deploy to Render" && git push origin master
```

### 🔗 Important Links

- **Render Dashboard**: https://dashboard.render.com
- **Your Deployment Guide**: See DEPLOYMENT_GUIDE.md for full details
- **Render Docs**: https://render.com/docs

### ⚠️ Common Issues

**Issue**: Build fails with module errors
- **Fix**: Make sure all imports have corresponding packages in requirements.txt

**Issue**: App crashes on startup  
- **Fix**: Check environment variables DB_FOLDER and IMAGE_FOLDER are set correctly

**Issue**: Images not loading
- **Fix**: Verify Images folder is committed to git and exists in repository

**Issue**: Free tier app takes long to load first time
- **Fix**: This is normal - free tier spins down after 15 mins of inactivity

### 🎯 Expected Result

After successful deployment:
- ✅ Web interface loads at your Render URL
- ✅ Face search works with uploaded images
- ✅ BIB search returns results
- ✅ Images display correctly
- ✅ Download button works

---

**Ready to deploy? Follow the full guide in DEPLOYMENT_GUIDE.md**
