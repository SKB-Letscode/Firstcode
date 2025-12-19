# Render Deployment Troubleshooting - Starter Plan

## You've upgraded to Starter Plan ✅
Now you should have enough resources to build successfully!

## Common "Exited with status 1" Fixes

### 1. Clear Build Cache
Sometimes old cache causes issues:
1. Go to Render Dashboard → Your Service
2. Click **"Manual Deploy"** dropdown
3. Select **"Clear build cache & deploy"**

### 2. Check Build Logs
Look for the specific error in build logs:

#### Error: "ModuleNotFoundError: No module named 'app'"
**Fix:** Added __init__.py files (already done in latest commit)

#### Error: "cmake: command not found"
**Fix:** Build script now installs cmake first

#### Error: "dlib build failed"
**Fix:** For Starter plan, this should work. If not, try:
```bash
# In Render Dashboard, set environment variable:
MAKEFLAGS=-j2
```

#### Error: "faiss-cpu installation failed"
**Fix:** Using faiss-cpu==1.8.0 (more stable than 1.13.0)

### 3. Environment Variables
Make sure these are set in Render Dashboard → Environment:

```
DB_FOLDER=/opt/render/project/src/DB
IMAGE_FOLDER=/opt/render/project/src/Images
PYTHON_VERSION=3.11.9
```

### 4. Build & Start Commands
Verify these in Render Dashboard → Settings:

**Build Command:**
```bash
bash render_build.sh
```

**Start Command:**
```bash
uvicorn app.server.api_services:service --host 0.0.0.0 --port $PORT
```

### 5. Python Version
Verify `runtime.txt` contains:
```
python-3.11.9
```

## 🔍 Debug Steps

### Step 1: Check Service Logs
1. Go to your service in Render
2. Click **"Logs"** tab
3. Look for the exact error message
4. Share the error here if still failing

### Step 2: Manual Deploy
1. Click **"Manual Deploy"**
2. Select **"Clear build cache & deploy"**
3. Watch the build process in real-time

### Step 3: Verify Files
Make sure these exist in your repo:
- ✅ Procfile
- ✅ requirements.txt
- ✅ render.yaml
- ✅ render_build.sh
- ✅ runtime.txt
- ✅ app/server/api_services.py
- ✅ app/server/__init__.py
- ✅ app/imgTools/__init__.py
- ✅ app/__init__.py
- ✅ DB folder with database files
- ✅ Images folder

## 🎯 Expected Build Time
With Starter plan:
- **5-10 minutes** - Normal (dlib takes time to compile)
- **15+ minutes** - Still OK, be patient
- **Timeout after 15 min** - Issue with build

## 📊 Build Success Indicators

You'll see these messages if successful:
```
=== Upgrading pip ===
✓ Successfully installed pip

=== Installing core dependencies ===
✓ Successfully installed numpy, Pillow, fastapi, uvicorn

=== Installing dlib ===
(This takes 5-10 minutes - be patient!)
✓ Successfully installed dlib

=== Installing face recognition ===
✓ Successfully installed face_recognition

=== Build completed successfully ===
All packages imported successfully!
```

Then deployment:
```
Starting service...
Application startup complete.
Uvicorn running on 0.0.0.0:10000
```

## 🚨 If Still Failing

### Try Alternative Build Command
Instead of `bash render_build.sh`, use direct pip:

```bash
pip install --no-cache-dir --upgrade pip setuptools wheel && pip install --no-cache-dir numpy==1.26.4 Pillow==10.4.0 fastapi==0.115.0 "uvicorn[standard]==0.30.0" requests==2.32.3 cmake && pip install --no-cache-dir dlib==19.24.6 && pip install --no-cache-dir face_recognition_models==0.3.0 face_recognition==1.3.0 faiss-cpu==1.8.0 boto3==1.35.0
```

### Check System Resources
During build, check if:
- Memory usage stays below plan limit
- CPU isn't timing out
- Disk space is sufficient

## ✅ Latest Changes (Just Pushed)

1. ✅ Switched to full api_services.py (with face search)
2. ✅ Updated Procfile to use full version
3. ✅ Updated render.yaml for Starter plan
4. ✅ Optimized render_build.sh
5. ✅ Added missing __init__.py files
6. ✅ Added verification step in build script

## 🆘 Need More Help?

Please share:
1. **Full error message** from build logs
2. **Which step** it fails at (pip install, starting service, etc.)
3. **Screenshot** of the error if possible

Then I can provide more specific help!

---

**Next Step:** Go to Render and trigger "Clear build cache & deploy"
