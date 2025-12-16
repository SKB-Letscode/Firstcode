# Deploying FMF Face Search to Render.com

## Prerequisites
1. GitHub account (to push your code)
2. Render.com account (free tier available)
3. AWS S3 bucket with your images and database

## Step 1: Prepare Your Code

### Update dbconnector.py for Cloud Deployment
Modify `app/dbconnector.py` to use environment variables:

```python
import os

# Use environment variables with fallbacks
local_db_folder = os.getenv('DB_FOLDER', r"C:\Work\FMF\DB")
LOCAL_IMAGE_FOLDER = os.getenv('IMAGE_FOLDER', r"C:\Work\FMF\Images")
bucket_name = os.getenv('S3_BUCKET_NAME', 'sara-s3-bucket')
```

### Install dlib dependency
Since dlib is commented out in requirements.txt, you need to add a buildpack or install it during build.
Update `requirements.txt` to include:
```
cmake==3.27.0
dlib==19.24.6
```

Or use the prebuilt binary:
```
https://github.com/charlielito/install-dlib-python-3.8/releases/download/v19.21.1/dlib-19.21.1-cp38-cp38-linux_x86_64.whl
```

## Step 2: Push Code to GitHub

```bash
# Initialize git if not already done
git init
git add .
git commit -m "Prepare for Render deployment"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

## Step 3: Deploy on Render

### Option A: Using render.yaml (Infrastructure as Code)

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" → "Blueprint"
3. Connect your GitHub repository
4. Render will detect `render.yaml` and set up the service
5. Add environment variables in the Render dashboard:
   - `AWS_ACCESS_KEY_ID`: Your AWS access key
   - `AWS_SECRET_ACCESS_KEY`: Your AWS secret key
   - `AWS_DEFAULT_REGION`: Your AWS region (e.g., us-east-1)

### Option B: Manual Setup

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: fmf-face-search-api
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.selfisearch.face_search_api:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free (or upgrade for better performance)

5. Add Environment Variables:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `S3_BUCKET_NAME`
   - `DB_FOLDER`: `/tmp/DB` (ephemeral, lost on restart)
   - `IMAGE_FOLDER`: `/tmp/Images` (ephemeral, lost on restart)

6. Set Health Check:
   - **Path**: `/health`

7. Click "Create Web Service"

**Note**: Free tier uses ephemeral storage - database and FAISS index files in `/tmp/` will be lost on restart. The app will need to download from S3 or rebuild on each restart. For persistent storage, upgrade to a paid plan that supports disks.

## Step 4: Post-Deployment Setup

### Initialize Database and Index
After deployment, trigger preprocessing to populate the database:

```bash
# Using curl or Postman
curl -X POST https://your-app.onrender.com/trigger-preprocessing
```

### Test the API
```bash
# Health check
curl https://your-app.onrender.com/health

# Search for a face
curl -X POST "https://your-app.onrender.com/search-face?similarity_threshold=0.5&top_k=3" \
  -F "file=@/path/to/test-image.jpg"
```

## Step 5: Monitoring and Logs

1. Go to your service in Render Dashboard
2. Click "Logs" to view real-time logs
3. Monitor metrics (CPU, Memory, Requests)

## Important Notes

### Free Tier Limitations
- **Spins down after 15 minutes of inactivity** (first request after spin-down takes ~30 seconds)
- **750 hours/month** of runtime
- **1 GB disk space**
- **512 MB RAM**

### Upgrade Recommendations for Production
- **Starter Plan** ($7/month): No spin-down, 512 MB RAM
- **Standard Plan** ($25/month): 2 GB RAM, better for face_recognition library
- **Disk**: Upgrade if you need more than 1 GB for images/DB

### Performance Tips
1. **Use S3 for images**: Don't store images on Render disk (expensive and limited)
2. **Cache FAISS index**: Load index once at startup, not per request
3. **Optimize images**: Downscale before processing
4. **Use async workers**: Offload CPU-bound tasks to thread pools

### Security
1. Never commit `.env` or credentials to git
2. Use Render's environment variable encryption
3. Consider using AWS IAM roles instead of access keys
4. Add CORS restrictions in production
5. Implement rate limiting for the API

## Troubleshooting

### Build Fails - dlib installation error
Add to `render_build.sh`:
```bash
apt-get update
apt-get install -y cmake g++ libopenblas-dev
```

### Face detection is slow/times out
- Upgrade to a plan with more RAM (face_recognition needs memory)
- Reduce image size before processing
- Consider using a GPU instance for CNN model

### Database not persisting
- Ensure disk is mounted correctly at `/opt/render/project/src/DB`
- Check write permissions

### App crashes on startup
- Check logs for import errors
- Verify all dependencies in requirements.txt
- Ensure DB/Images folders exist

## Alternative: Deploy on AWS (Better for this workload)

Consider AWS Elastic Beanstalk, ECS, or Lambda + API Gateway for:
- Better integration with S3
- More RAM for face_recognition
- GPU support for CNN detection
- Better price/performance for CPU-intensive workloads

## Support

For issues, check:
- Render Docs: https://render.com/docs
- Render Community: https://community.render.com/
- GitHub Issues for this project
