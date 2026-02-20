#!/bin/bash
#====================================================================================
# FMF Application - EC2 Deployment Script
# Author: Deployment Assistant
# Description: Automates deployment of FMF app on Ubuntu EC2 instance
# Usage: sudo bash deploy_ec2.sh
#====================================================================================

set -e  # Exit on error

echo "=========================================="
echo "FMF Application Deployment Script"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_DIR="/home/ubuntu/fmf-app"
APP_USER="ubuntu"
VENV_DIR="$APP_DIR/venv"
SERVICE_NAME="fmf-app"

# Function to print colored messages
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    print_error "Please run as root (use sudo)"
    exit 1
fi

# Step 1: System Update
print_info "Step 1: Updating system packages..."
apt-get update
apt-get upgrade -y

# Step 2: Install System Dependencies
print_info "Step 2: Installing system dependencies..."
apt-get install -y \
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
    curl \
    htop

# Step 3: Install AWS CLI
if ! command -v aws &> /dev/null; then
    print_info "Step 3: Installing AWS CLI..."
    cd /tmp
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    unzip -q awscliv2.zip
    ./aws/install
    rm -rf aws awscliv2.zip
else
    print_info "Step 3: AWS CLI already installed, skipping..."
fi

# Step 4: Check if app directory exists
if [ ! -d "$APP_DIR" ]; then
    print_error "Application directory not found: $APP_DIR"
    print_info "Please upload your application files to $APP_DIR first"
    print_info "You can use: scp -r /path/to/app ubuntu@ec2-ip:$APP_DIR"
    exit 1
fi

# Step 5: Create Virtual Environment
print_info "Step 5: Creating Python virtual environment..."
cd $APP_DIR
if [ ! -d "$VENV_DIR" ]; then
    sudo -u $APP_USER python3.11 -m venv venv
else
    print_warning "Virtual environment already exists, skipping..."
fi

# Step 6: Install Python Dependencies
print_info "Step 6: Installing Python dependencies (this may take 10-15 minutes)..."
sudo -u $APP_USER bash << EOF
source $VENV_DIR/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r $APP_DIR/requirements_minimal.txt
EOF

# Step 7: Create Required Directories
print_info "Step 7: Creating required directories..."
mkdir -p $APP_DIR/DB
mkdir -p $APP_DIR/Images/Downloads/Thumbnails
mkdir -p $APP_DIR/Images/Images
chown -R $APP_USER:$APP_USER $APP_DIR

# Step 8: Create Environment File if it doesn't exist
if [ ! -f "$APP_DIR/.env" ]; then
    print_info "Step 8: Creating .env file template..."
    cat > $APP_DIR/.env << 'ENVEOF'
# Image and Database Folders
IMAGE_FOLDER=/home/ubuntu/fmf-app/Images
DB_FOLDER=/home/ubuntu/fmf-app/DB

# AWS S3 Settings (optional - uncomment and configure if using S3)
# AWS_ACCESS_KEY_ID=your_access_key
# AWS_SECRET_ACCESS_KEY=your_secret_key
# AWS_REGION=us-east-1
# S3_BUCKET_NAME=your-bucket-name

# Application Settings
PORT=8000
ENVEOF
    chown $APP_USER:$APP_USER $APP_DIR/.env
    print_warning "Please edit $APP_DIR/.env with your configuration"
else
    print_info "Step 8: .env file already exists, skipping..."
fi

# Step 9: Create Systemd Service
print_info "Step 9: Creating systemd service..."
cat > /etc/systemd/system/$SERVICE_NAME.service << 'SERVICEEOF'
[Unit]
Description=FMF Face Recognition & BIB Search API
After=network.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/fmf-app
Environment="PATH=/home/ubuntu/fmf-app/venv/bin"
EnvironmentFile=/home/ubuntu/fmf-app/.env
ExecStart=/home/ubuntu/fmf-app/venv/bin/uvicorn app.server.api_services_minimal:service --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SERVICEEOF

# Step 10: Configure Nginx
print_info "Step 10: Configuring Nginx..."
cat > /etc/nginx/sites-available/$SERVICE_NAME << 'NGINXEOF'
server {
    listen 80;
    server_name _;

    client_max_body_size 20M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
NGINXEOF

# Enable Nginx site
ln -sf /etc/nginx/sites-available/$SERVICE_NAME /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
nginx -t

# Step 11: Configure Firewall
print_info "Step 11: Configuring firewall..."
ufw --force enable
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw status

# Step 12: Enable and Start Services
print_info "Step 12: Enabling and starting services..."
systemctl daemon-reload
systemctl enable $SERVICE_NAME
systemctl restart nginx
systemctl start $SERVICE_NAME

# Wait a moment for service to start
sleep 3

# Step 13: Check Status
print_info "Step 13: Checking service status..."
systemctl status $SERVICE_NAME --no-pager || true

echo ""
echo "=========================================="
print_info "Deployment Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit configuration: sudo nano $APP_DIR/.env"
echo "2. If using S3, configure AWS credentials: aws configure"
echo "3. Restart service: sudo systemctl restart $SERVICE_NAME"
echo "4. Check logs: sudo journalctl -u $SERVICE_NAME -f"
echo "5. Access application: http://$(curl -s ifconfig.me)"
echo ""
echo "Useful commands:"
echo "  - View logs: sudo journalctl -u $SERVICE_NAME -f"
echo "  - Restart app: sudo systemctl restart $SERVICE_NAME"
echo "  - Stop app: sudo systemctl stop $SERVICE_NAME"
echo "  - Check status: sudo systemctl status $SERVICE_NAME"
echo ""
