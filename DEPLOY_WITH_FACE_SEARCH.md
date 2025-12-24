# Deploy to Render with Face Search Feature

## Changes Made (24-Dec-2025)

### 1. Updated `api_services_minimal.py`
- ✅ Added face search endpoint with memory optimizations
- ✅ Added FAISS index and metadata loading
- ✅ Lazy loading of face_recognition to save memory
- ✅ Image resizing (MAX_DIM=800) before processing
- ✅ Distance threshold (0.19) to limit results
- ✅ Graceful fallback if face search fails

### 2. Updated `requirements_minimal.txt`
- ✅ Added face_recognition dependencies:
  - dlib==19.24.6
  - face_recognition_models==0.3.0
  - face_recognition==1.3.0
- ✅ All other dependencies remain the same

### 3. Configuration Files (Already Set)
- ✅ `render.yaml` - Uses requirements_minimal.txt
- ✅ `Procfile` - Uses api_services_minimal.py
- ✅ `runtime.txt` - Python 3.11.9

## Deployment Steps

### Step 1: Test Locally (Optional but Recommended)

```powershell
# In your Server terminal
.\venv\Scripts\Activate.ps1
cd C:\Work\FMF

# Install updated requirements
pip install -r requirements_minimal.txt

# Test the server
uvicorn app.server.api_services_minimal:service --reload

# Open browser to http://127.0.0.1:8000
# Test both BIB search and Face search
```

### Step 2: Commit and Push Changes

```powershell
# In your Common terminal
git add .
git commit -m "Added face search feature with memory optimizations for Render Starter plan"
git push origin master
```

### Step 3: Deploy to Render

#### Option A: Auto-Deploy (if enabled)
- Render will automatically detect the push and start deploying
- Monitor the build logs in Render dashboard

#### Option B: Manual Deploy
1. Go to https://dashboard.render.com/
2. Find your service: `fmf-face-search-api`
3. Click "Manual Deploy" → "Deploy latest commit"

### Step 4: Monitor Deployment

Watch the build logs for:
1. ✅ Package installation (dlib takes 5-10 minutes)
2. ✅ S3 file download (DB, FAISS index, metadata)
3. ✅ "Successfully loaded FAISS index with X faces"
4. ✅ Service starts on port

### Step 5: Verify Deployment

Once deployed, test these endpoints:

```bash
# Health check
https://your-app-name.onrender.com/health

# Should return:
{
  "status": "ok",
  "mode": "Full featured (Face + BIB search)",
  "face_search_enabled": true,
  ...
}
```

## Memory Optimization Features

### Why This Works on Starter Plan (512MB RAM)

1. **Pre-computed FAISS Index**: No training/encoding at startup
2. **Lazy Loading**: face_recognition imported only when needed
3. **Image Resizing**: All images resized to max 800px before processing
4. **Distance Threshold**: Only returns high-confidence matches
5. **Temporary Files**: Cleaned up immediately after use

### Expected Memory Usage

- Startup: ~200MB (loading FAISS index + dependencies)
- Face Search Request: +100-150MB (spike during processing)
- Total Peak: ~350-400MB (well within 512MB limit)

## Troubleshooting

### Build Fails

**Error**: Out of memory during pip install
**Solution**: This shouldn't happen with requirements_minimal.txt, but if it does:
1. Check Render logs for the specific package failing
2. The render_build.sh script has step-by-step installation if needed

**Error**: dlib installation fails
**Solution**: 
- Render should have cmake installed
- Check build logs for cmake errors

### Runtime Issues

**Error**: "FAISS index not loaded"
**Solution**:
1. Check S3 credentials in Render environment variables
2. Verify files exist in S3: `1_ImageDB.sqlite`, `1_faiss_face_index.bin`, `1_face_metadata.pkl`
3. Check startup logs for S3 download errors

**Error**: "No face detected"
**Solution**: This is normal - user needs to upload a clear face image

**Error**: Out of memory during face search
**Solution**: This is unlikely with our optimizations, but if it happens:
1. Reduce MAX_DIM from 800 to 600 in api_services_minimal.py
2. Reduce top_k parameter (default is 5)

## Configuration Reference

### Current Settings (Optimized)
```python
MAX_DIM = 800              # Resize images to 800px max
DISTANCE_THRESHOLD = 0.19   # Only return good matches
top_k = 5                  # Return top 5 matches
```

### Environment Variables (Set in Render Dashboard)
```
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_DEFAULT_REGION=us-east-1
S3_BUCKET_NAME=sara-s3-bucket
DB_FOLDER=/opt/render/project/src/DB
IMAGE_FOLDER=/opt/render/project/src/Images
```

## Post-Deployment

### Test Face Search
1. Go to your deployed URL
2. Select an event
3. Upload a selfie
4. Click "Search Photos"
5. Should see matching photos with similarity scores

### Test BIB Search
1. Go to "Search by BIB" tab
2. Enter a BIB number
3. Should see all photos with that BIB

### Monitor Performance
- Check Render metrics for memory usage
- Should stay under 400MB during normal operation
- Response time: 2-5 seconds for face search

## Success Indicators

✅ Build completes in 10-15 minutes
✅ Service starts without errors
✅ Health check shows "face_search_enabled": true
✅ Face search returns results
✅ BIB search still works
✅ Memory usage < 400MB

## Next Steps

Once deployed successfully:
1. Test with various face images
2. Test with different BIB numbers
3. Monitor memory usage for 24 hours
4. Share the URL with users!

## Support

If you encounter any issues:
1. Check Render logs for errors
2. Test /health endpoint
3. Verify S3 files are accessible
4. Check environment variables in Render dashboard

---

**Deployment Date**: 24-Dec-2025
**Version**: Full Featured (Face + BIB Search)
**Plan**: Render Starter (512MB RAM)
**Status**: Ready to Deploy! 🚀
