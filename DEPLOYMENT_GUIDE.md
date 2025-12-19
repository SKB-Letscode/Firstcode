# Find My Photos - Render Deployment Guide

This guide will help you deploy your Face Search application to Render for public access.

## 📋 Prerequisites

1. **GitHub Account** - Your code needs to be in a GitHub repository
2. **Render Account** - Sign up at [https://render.com](https://render.com) (free tier available)
3. **Required Files** (already in your project):
   - `app/server/api_services.py` - Main API service
   - `app/web/index.html` - Web interface
   - `app/dbconnector.py` - Database configuration
   - `DB/1_ImageDB.sqlite` - SQLite database
   - `DB/1_faiss_face_index.bin` - FAISS index
   - `DB/1_face_metadata.pkl` - Face metadata
   - `Images/` - Image folder with thumbnails and support files
   - `requirements.txt` - Python dependencies
   - `Procfile` - Render startup command
   - `render.yaml` - Render configuration

## 🚀 Step-by-Step Deployment

### Step 1: Prepare Your GitHub Repository

1. **Commit all changes** to your GitHub repository:
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin master
   ```

2. **Verify these files are in your repository:**
   - ✅ Procfile
   - ✅ requirements.txt
   - ✅ render.yaml
   - ✅ app/ folder
   - ✅ DB/ folder (with .sqlite, .bin, .pkl files)
   - ✅ Images/ folder

### Step 2: Create Render Account & Connect GitHub

1. Go to [https://render.com](https://render.com)
2. Click **"Get Started"** or **"Sign Up"**
3. Choose **"Sign up with GitHub"**
4. Authorize Render to access your GitHub repositories

### Step 3: Create New Web Service

1. From Render Dashboard, click **"New +"** → **"Web Service"**
2. Click **"Connect a repository"**
3. Find and select your repository: **SKB-Letscode/Firstcode**
4. Click **"Connect"**

### Step 4: Configure Web Service

Fill in the following settings:

#### Basic Settings:
- **Name**: `fmf-face-search` (or your preferred name)
- **Region**: Choose closest to your users (e.g., Oregon, Frankfurt)
- **Branch**: `master` (or `main` if that's your default)
- **Root Directory**: Leave blank
- **Runtime**: **Python 3**

#### Build & Deploy Settings:
- **Build Command**: 
  ```bash
  pip install -r requirements.txt
  ```

- **Start Command**: 
  ```bash
  uvicorn app.server.api_services:service --host 0.0.0.0 --port $PORT
  ```

#### Instance Type:
- **Free** (for testing) or **Starter** ($7/month for better performance)

### Step 5: Set Environment Variables

Click **"Advanced"** and add these environment variables:

| Key | Value | Description |
|-----|-------|-------------|
| `PYTHON_VERSION` | `3.11.9` | Python version |
| `DB_FOLDER` | `/opt/render/project/src/DB` | Database folder path |
| `IMAGE_FOLDER` | `/opt/render/project/src/Images` | Images folder path |

**Optional AWS S3 variables** (if using S3 for images):
- `AWS_ACCESS_KEY_ID` - Your AWS access key
- `AWS_SECRET_ACCESS_KEY` - Your AWS secret key (keep secret!)
- `AWS_DEFAULT_REGION` - e.g., `us-east-1`
- `S3_BUCKET_NAME` - Your S3 bucket name

### Step 6: Deploy

1. Click **"Create Web Service"**
2. Render will start building your application
3. Watch the deployment logs for any errors
4. Wait for status to show **"Live"** (usually 5-10 minutes)

### Step 7: Access Your Application

Once deployed, you'll get a URL like:
```
https://fmf-face-search.onrender.com
```

- **Web Interface**: `https://your-app.onrender.com/`
- **API Docs**: `https://your-app.onrender.com/docs`
- **Health Check**: `https://your-app.onrender.com/health`

## 📱 Update index.html for Production

After deployment, update your `index.html` to use the production API URL:

1. Open [app/web/index.html](app/web/index.html)
2. Find this line (around line 463):
   ```javascript
   const API_BASE = 'http://localhost:8000';
   ```
3. Change it to your Render URL:
   ```javascript
   const API_BASE = 'https://fmf-face-search.onrender.com';
   ```
4. Commit and push:
   ```bash
   git add app/web/index.html
   git commit -m "Update API URL for production"
   git push origin master
   ```

Render will automatically redeploy with the new changes!

## ⚙️ Important Notes

### Free Tier Limitations:
- **Spins down after 15 minutes of inactivity**
- First request after spin-down takes ~30-60 seconds
- 750 hours/month free
- Perfect for testing and demos

### Upgrade to Starter ($7/month) for:
- ✅ Always-on service (no spin-down)
- ✅ Faster performance
- ✅ Better for production use

### Storage Considerations:
Your app includes database and image files. Render's free tier includes:
- **Limited disk space** on the instance
- Files are **ephemeral** (lost on redeploy)

**Recommendation**: For production, consider:
1. Use AWS S3 for images (already partially configured in your code)
2. Use a persistent database service for SQLite data
3. Or upgrade to a paid plan with persistent disk

## 🔧 Troubleshooting

### Build Fails
- Check Python version in `runtime.txt` matches your local version
- Verify all dependencies are in `requirements.txt`
- Check build logs for specific error messages

### App Crashes on Startup
- Verify `DB_FOLDER` and `IMAGE_FOLDER` paths are correct
- Check that DB files exist in the repository
- Review application logs in Render dashboard

### Can't Access Web Interface
- Ensure index.html exists in `app/web/`
- Check that StaticFiles mounting is correct in `api_services.py`
- Verify CORS settings allow browser access

### Images Not Loading
- Check `THUMBNAILS_FOLDER` path in `api_services.py`
- Verify Images folder is committed to repository
- Check file permissions and paths in logs

## 📊 Monitoring

In Render Dashboard:
- **Logs**: View real-time application logs
- **Metrics**: CPU, memory usage (paid plans)
- **Events**: Deployment history
- **Shell**: Access terminal (paid plans)

## 🔄 Auto-Deploy

Render automatically deploys when you push to your connected branch:

```bash
# Make changes
git add .
git commit -m "Your changes"
git push origin master

# Render automatically deploys!
```

## 📞 Support

- **Render Docs**: [https://render.com/docs](https://render.com/docs)
- **Render Community**: [https://community.render.com](https://community.render.com)
- **FastAPI Docs**: [https://fastapi.tiangolo.com](https://fastapi.tiangolo.com)

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Render account created and GitHub connected
- [ ] Web service created in Render
- [ ] Environment variables configured
- [ ] Build completed successfully
- [ ] Service shows "Live" status
- [ ] Web interface accessible
- [ ] Face search working
- [ ] BIB search working
- [ ] Images loading correctly
- [ ] Production API URL updated in index.html
- [ ] Final deployment with production URL

---

**🎉 Congratulations! Your Face Search app is now publicly accessible!**

Share your app URL with others: `https://your-app.onrender.com`
