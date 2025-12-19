# Render "Exited with status 1" - Solutions

## The Problem
Render free tier has **512MB RAM limit** during builds. Installing `dlib` and `face_recognition` requires **2-4GB**, causing build failures.

## ✅ Solution 1: Upgrade to Starter Plan (RECOMMENDED - $7/month)

**This is the best solution** - gives you 2GB+ RAM for builds.

### Steps:
1. In Render Dashboard, go to your service
2. Click **"Settings"** → **"Instance Type"**
3. Change from **"Free"** to **"Starter"**
4. Click **"Save Changes"**
5. Trigger **"Manual Deploy"**

**Benefits:**
- ✅ All features work (face search + BIB search)
- ✅ No spin-down (always available)
- ✅ Faster performance
- ✅ SSL certificate included

---

## ✅ Solution 2: Deploy BIB Search Only (FREE TIER)

Deploy without face recognition - only BIB search works.

### Steps:

1. **Update Procfile:**
   ```
   web: uvicorn app.server.api_services_minimal:service --host 0.0.0.0 --port $PORT
   ```

2. **Update render.yaml:**
   ```yaml
   buildCommand: pip install -r requirements_minimal.txt
   startCommand: uvicorn app.server.api_services_minimal:service --host 0.0.0.0 --port $PORT
   ```

3. **Commit and push:**
   ```powershell
   git add .
   git commit -m "Deploy minimal version for free tier"
   git push origin master
   ```

**What works:**
- ✅ BIB number search
- ✅ Event browsing
- ✅ Image display
- ✅ Download
- ❌ Face search (disabled with message to upgrade)

---

## ✅ Solution 3: Use Alternative Platform

Deploy to platforms with more generous free tiers:

### Railway.app
- **Free tier**: $5 credit/month (500 hours)
- More build resources
- Similar to Render

### Steps:
1. Sign up at https://railway.app
2. Connect GitHub repo
3. Use same configuration (Procfile, requirements.txt)
4. Deploy

### Fly.io
- **Free tier**: 3GB RAM for builds
- More generous than Render
- Good for Python apps

---

## ✅ Solution 4: Pre-built Docker Image

Use Docker with pre-compiled wheels to avoid building dlib.

### Create Dockerfile:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    cmake \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.server.api_services:service", "--host", "0.0.0.0", "--port", "8000"]
```

### Deploy:
1. In Render, choose **"Docker"** instead of **"Python"**
2. It will use your Dockerfile
3. More resources available for Docker builds

---

## 🎯 Quick Decision Guide

| Your Situation | Best Solution |
|----------------|---------------|
| Want all features + reliable performance | **Solution 1: Upgrade to Starter ($7/mo)** |
| Only need BIB search, free tier OK | **Solution 2: Minimal deployment** |
| Willing to try other platforms | **Solution 3: Railway or Fly.io** |
| Have Docker experience | **Solution 4: Docker deployment** |

---

## 🚀 Immediate Action (Choose One)

### Option A: Upgrade (Full Features)
```powershell
# No code changes needed
# Just upgrade in Render Dashboard → Settings → Instance Type → Starter
```

### Option B: Minimal Deployment (Free, BIB only)
```powershell
# Update Procfile
echo "web: uvicorn app.server.api_services_minimal:service --host 0.0.0.0 --port `$PORT" > Procfile

# Commit and push
git add Procfile
git commit -m "Use minimal API for free tier"
git push origin master
```

---

## 📊 Cost Comparison

| Platform | Free Tier Build RAM | Monthly Cost for More RAM |
|----------|---------------------|---------------------------|
| Render | 512MB | $7 (Starter - 2GB) |
| Railway | 8GB | $5 credit = 500 hrs |
| Fly.io | 3GB | $0 (free tier works) |
| Heroku | 512MB | $7 (Eco dyno) |

---

## ❓ FAQ

**Q: Why does it fail?**
A: Building `dlib` from source needs 2-4GB RAM. Free tier only has 512MB.

**Q: Can I use pre-built wheels?**
A: PyPI doesn't have pre-built dlib wheels for Linux. Must build from source.

**Q: Is $7/month worth it?**
A: Yes - you get face search, no downtime, faster performance, SSL.

**Q: Will minimal version work well?**
A: Yes, BIB search and browsing work perfectly. Only face upload search is disabled.

---

## 🆘 Still Need Help?

1. Try **Solution 1** (upgrade) - easiest and most reliable
2. Or try **Solution 2** (minimal) - free but limited
3. Contact me with build logs if issues persist

---

**Recommendation: Upgrade to Starter plan for best experience!**
