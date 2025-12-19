# Render Memory Issues - Solutions Guide

## Problem
Ran out of memory (used over 8GB) while building your code on Render.

## Root Cause
Heavy packages like `dlib`, `face_recognition`, and `faiss-cpu` require significant memory during installation, especially when building from source.

## Solution 1: Optimized Build (Implemented) ✅

I've already updated your files with these optimizations:

### Changes Made:
1. **requirements.txt** - Optimized package order and versions
2. **render_build.sh** - Install packages sequentially with `--no-cache-dir` flag
3. **render.yaml** - Use the custom build script

### What This Does:
- Installs packages one at a time instead of all at once
- Uses `--no-cache-dir` to reduce memory usage
- Installs dependencies in optimal order
- Uses a lighter version of FAISS (1.8.0 instead of 1.13.0)

## Solution 2: If Still Failing - Upgrade Plan

If the optimized build still fails on the free tier:

### Option A: Use Render Starter Plan ($7/month)
- More memory for builds (512MB → 2GB+ RAM)
- Faster builds
- No spin-down
- Update `render.yaml`:
  ```yaml
  plan: starter  # instead of free
  ```

## Solution 3: Pre-built Docker Image (Advanced)

If you keep hitting memory limits, consider using Docker with pre-built wheels:

1. Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Start command
CMD ["uvicorn", "app.server.api_services:service", "--host", "0.0.0.0", "--port", "8000"]
```

2. Deploy as Docker service instead of Python service

## Solution 4: Split Dependencies (If needed)

Create a minimal `requirements_render.txt` without heavy packages:

```txt
fastapi==0.115.0
uvicorn[standard]==0.30.0
Pillow==10.4.0
numpy==1.26.4
requests==2.32.3
boto3==1.35.0
```

Then pre-compute your FAISS index and upload DB files, removing the need for face_recognition during deployment.

## Recommended Action Now

1. **Commit and push the updated files:**
   ```powershell
   git add requirements.txt render_build.sh render.yaml
   git commit -m "Optimize build for Render memory limits"
   git push origin master
   ```

2. **Try deploying again** with the optimized build

3. **If it still fails:**
   - Upgrade to Starter plan ($7/month) - Most reliable solution
   - Or use the Docker approach

## Quick Deploy Steps

```powershell
# Commit optimized build files
git add .
git commit -m "Fix Render memory issues"
git push origin master

# Then in Render Dashboard:
# - Trigger Manual Deploy
# - Or create new service with optimized settings
```

## Build Command in Render Dashboard

Use this in the Build Command field:
```bash
bash render_build.sh
```

Or if the script has issues:
```bash
pip install --no-cache-dir --upgrade pip setuptools wheel && \
pip install --no-cache-dir fastapi uvicorn[standard] numpy==1.26.4 Pillow==10.4.0 && \
pip install --no-cache-dir cmake dlib==19.24.6 && \
pip install --no-cache-dir face_recognition_models==0.3.0 face_recognition==1.3.0 && \
pip install --no-cache-dir faiss-cpu==1.8.0 boto3==1.35.0 requests==2.32.3
```

## Success Indicators

✅ Build completes without memory errors
✅ All packages installed successfully
✅ Service starts and shows "Live" status
✅ Health check passes

## Still Having Issues?

Contact me with the error logs and we'll try the next solution!
