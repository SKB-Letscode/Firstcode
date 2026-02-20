# AWS EC2 Deployment Guide

This guide will help you deploy the Face Recognition & BIB Search application on an AWS EC2 instance.

## Prerequisites

- AWS Account with EC2 access
- Basic knowledge of SSH and Linux commands
- (Optional) S3 bucket with your database files and FAISS indices
- (Optional) Domain name for production deployment

## Recommended EC2 Instance Types

Given the application's memory requirements (face_recognition, dlib, FAISS):
- **Minimum**: t3.small (2GB RAM) - Recommended
- **Budget**: t2.micro (1GB RAM) - May struggle with face recognition
- **Better**: t3.medium (4GB RAM) - For production use

> ⚠️ **Note**: t4.micro doesn't exist. I assume you meant t3.micro or t2.micro.
> For this application with face_recognition and dlib, **t3.small is strongly recommended**.

## Step 1: Launch EC2 Instance

### 1.1 Create EC2 Instance
1. Go to AWS Console → EC2 → Launch Instance
2. **Name**: `fmf-app-server` (or your choice)
3. **AMI**: Ubuntu Server 22.04 LTS (64-bit x86)
4. **Instance Type**: t3.small
5. **Key Pair**: Create new or select existing key pair
6. **Network Settings**:
   - Allow SSH (port 22) from your IP
   - Allow HTTP (port 80) from anywhere (0.0.0.0/0)
   - Allow HTTPS (port 443) from anywhere (optional)
   - Allow Custom TCP (port 8000) from anywhere (for testing)

### 1.2 Configure Storage
- Minimum: 20 GB gp3 SSD
- Recommended: 30 GB for databases and images

### 1.3 Launch and Connect
```bash
# Download your key pair (e.g., my-key.pem) and set permissions
chmod 400 my-key.pem

# Connect to your instance
ssh -i my-key.pem ubuntu@<your-ec2-public-ip>
```

## Step 2: Server Initial Setup

### 2.1 Update System
```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### 2.2 Install System Dependencies
```bash
# Install essential build tools
sudo apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    cmake \
    build-essential \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    git \
    nginx \
    sqlite3 \
    unzip \
    curl

# Install AWS CLI (for S3 access)
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
rm -rf aws awscliv2.zip
```

## Step 3: Deploy Application

### 3.1 Clone or Upload Application
```bash
# Option 1: Clone from Git (if you have a repo)
cd /home/ubuntu
git clone https://github.com/SKB-Letscode/Firstcode.git fmf-app
cd fmf-app

# Option 2: Upload via SCP from your local machine
# (Run this from your local machine)
scp -i my-key.pem -r c:\Work\FMF ubuntu@<your-ec2-public-ip>:/home/ubuntu/fmf-app
```

### 3.2 Create Python Virtual Environment
```bash
cd /home/ubuntu/fmf-app
python3.11 -m venv venv
source venv/bin/activate
```

### 3.3 Install Python Dependencies
```bash
# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install dependencies (this will take 10-15 minutes)
pip install -r requirements.txt

# Or for minimal deployment (without some features)
# pip install -r requirements_minimal.txt
```

### 3.4 Configure Environment Variables
```bash
# Create .env file
nano .env
```

Add the following (adjust as needed):
```env
# Image and Database Folders
IMAGE_FOLDER=/home/ubuntu/fmf-app/Images
DB_FOLDER=/home/ubuntu/fmf-app/DB

# AWS S3 (if using S3 for storage)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name

# Application Settings
PORT=8000
```

Save and exit (Ctrl+X, then Y, then Enter)

### 3.5 Create Required Directories
```bash
mkdir -p /home/ubuntu/fmf-app/DB
mkdir -p /home/ubuntu/fmf-app/Images/Downloads/Thumbnails
mkdir -p /home/ubuntu/fmf-app/Images/Images
```

### 3.6 Download S3 Files (if applicable)
If your database files are stored in S3:
```bash
# Configure AWS credentials
aws configure

# Download files
python3 -c "from app.s3_downloader import download_from_s3; download_from_s3()"
```

## Step 4: Test Application

### 4.1 Manual Test
```bash
cd /home/ubuntu/fmf-app
source venv/bin/activate
uvicorn app.server.api_services_minimal:service --host 0.0.0.0 --port 8000
```

Open browser: `http://<your-ec2-public-ip>:8000`

Press Ctrl+C to stop.

## Step 5: Setup Systemd Service (Production)

### 5.1 Create Service File
```bash
sudo nano /etc/systemd/system/fmf-app.service
```

Copy contents from the `fmf-app.service` file (see deployment files).

### 5.2 Enable and Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable fmf-app
sudo systemctl start fmf-app
sudo systemctl status fmf-app
```

### 5.3 Check Logs
```bash
sudo journalctl -u fmf-app -f
```

## Step 6: Setup Nginx Reverse Proxy

### 6.1 Configure Nginx
```bash
sudo nano /etc/nginx/sites-available/fmf-app
```

Copy contents from `nginx-fmf.conf` (see deployment files).

### 6.2 Enable Site
```bash
sudo ln -s /etc/nginx/sites-available/fmf-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

Now access: `http://<your-ec2-public-ip>`

## Step 7: Configure Security & Monitoring

### 7.1 Setup Firewall (UFW)
```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 7.2 Monitor Application
```bash
# Check service status
sudo systemctl status fmf-app

# View logs
sudo journalctl -u fmf-app -f

# Check resource usage
htop
```

## Step 8: (Optional) Setup SSL with Let's Encrypt

If you have a domain name:
```bash
sudo apt-get install certbot python3-certbot-nginx -y
sudo certbot --nginx -d yourdomain.com
```

## Updating the Application

```bash
cd /home/ubuntu/fmf-app
git pull  # or upload new files
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart fmf-app
```

## Troubleshooting

### Application won't start
```bash
# Check logs
sudo journalctl -u fmf-app -n 100

# Check if port is in use
sudo lsof -i :8000

# Check permissions
ls -la /home/ubuntu/fmf-app
```

### Out of Memory
- Upgrade to t3.small or larger
- Add swap space:
```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### Database not found
- Check DB_FOLDER path in .env
- Ensure files downloaded from S3
- Check permissions: `sudo chown -R ubuntu:ubuntu /home/ubuntu/fmf-app`

## Cost Optimization

1. **Stop instance when not in use**: EC2 → Stop Instance
2. **Use Elastic IP**: Prevent IP changes on stop/start
3. **Set up CloudWatch alarms**: Monitor usage and costs
4. **Use Reserved Instances**: If running 24/7 for 1+ year

## Security Best Practices

1. Regularly update system: `sudo apt-get update && sudo apt-get upgrade`
2. Use security groups to restrict access
3. Don't commit AWS credentials to Git
4. Use IAM roles instead of access keys when possible
5. Enable CloudWatch logging
6. Regular backups of DB folder

## Support

For issues, contact the development team or check application logs.
