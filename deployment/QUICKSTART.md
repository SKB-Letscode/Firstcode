# Quick Start Guide - AWS EC2 Deployment

## 🚀 Quick Deployment (5 Steps)

### 1️⃣ Launch EC2 Instance
```bash
# From AWS Console:
- AMI: Ubuntu 22.04 LTS
- Instance Type: t3.small (recommended) or t2.small
- Storage: 20-30 GB
- Security Groups: Allow ports 22, 80, 443, 8000
```

### 2️⃣ Connect to Instance
```bash
ssh -i your-key.pem ubuntu@<EC2-PUBLIC-IP>
```

### 3️⃣ Upload Application Files
```bash
# From your local machine (Windows PowerShell):
scp -i your-key.pem -r C:\Work\FMF ubuntu@<EC2-PUBLIC-IP>:/home/ubuntu/fmf-app
```

### 4️⃣ Run Deployment Script
```bash
# On EC2 instance:
cd /home/ubuntu/fmf-app
sudo bash deploy_ec2.sh
```

### 5️⃣ Configure & Access
```bash
# Edit environment file:
sudo nano /home/ubuntu/fmf-app/.env

# Restart service:
sudo systemctl restart fmf-app

# Access your app:
# Open browser: http://<EC2-PUBLIC-IP>
```

---

## 📋 Pre-Deployment Checklist

- [ ] AWS account with EC2 access
- [ ] SSH key pair downloaded (.pem file)
- [ ] Application files ready (this folder)
- [ ] (Optional) S3 bucket set up for database files
- [ ] (Optional) Domain name for production

---

## 🛠️ Useful Commands

```bash
# View logs in real-time
sudo journalctl -u fmf-app -f

# Restart application
sudo systemctl restart fmf-app

# Check status
sudo systemctl status fmf-app

# Stop application
sudo systemctl stop fmf-app

# Start application
sudo systemctl start fmf-app

# Check resource usage
htop

# Test nginx configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

---

## 🔧 Common Issues & Solutions

### Issue: Application won't start
```bash
# Check logs for errors
sudo journalctl -u fmf-app -n 100 --no-pager

# Check if Python dependencies installed
source /home/ubuntu/fmf-app/venv/bin/activate
pip list
```

### Issue: Can't access from browser
```bash
# Check if service is running
sudo systemctl status fmf-app

# Check if port is open
sudo lsof -i :8000

# Check firewall
sudo ufw status

# Check AWS Security Group allows port 80
```

### Issue: Out of memory
```bash
# Check memory usage
free -h

# Add swap space (2GB):
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### Issue: Database files not found
```bash
# Check if DB folder exists
ls -la /home/ubuntu/fmf-app/DB/

# If using S3, download files:
aws configure
python3 -c "from app.s3_downloader import download_from_s3; download_from_s3()"
```

---

## 📊 Monitoring

```bash
# CPU and Memory usage
htop

# Disk usage
df -h

# Application logs
sudo journalctl -u fmf-app -f

# Nginx logs
sudo tail -f /var/log/nginx/fmf-app-access.log
sudo tail -f /var/log/nginx/fmf-app-error.log

# System logs
sudo tail -f /var/log/syslog
```

---

## 🔒 Security Checklist

- [ ] UFW firewall enabled
- [ ] SSH key-based authentication only
- [ ] Unnecessary ports closed in Security Group
- [ ] .env file not committed to git
- [ ] AWS credentials using IAM roles (not access keys)
- [ ] Regular system updates scheduled
- [ ] SSL certificate installed (for production)
- [ ] Application logs monitored

---

## 💰 Cost Optimization

1. **Stop when not needed**: Stop EC2 instance when not in use (you only pay for storage)
2. **Use Elastic IP**: Prevent IP address changes (small cost)
3. **Reserved Instances**: If running 24/7 for 1+ year
4. **Auto Scaling**: Scale down during low traffic

**Estimated Monthly Costs** (us-east-1):
- t3.small: ~$15/month (24/7)
- Storage 30GB: ~$3/month
- Data transfer: Variable
- **Total: ~$18-25/month**

---

## 📚 Additional Resources

- Full Documentation: `DEPLOYMENT_AWS_EC2.md`
- Nginx Config: `deployment/nginx-fmf.conf`
- Service File: `deployment/fmf-app.service`
- Environment Template: `deployment/.env.template`

---

## 🆘 Getting Help

1. Check logs: `sudo journalctl -u fmf-app -f`
2. Review full documentation: `DEPLOYMENT_AWS_EC2.md`
3. Check application status: `sudo systemctl status fmf-app`
4. Verify environment variables: `cat /home/ubuntu/fmf-app/.env`

---

**Need more help?** Refer to `DEPLOYMENT_AWS_EC2.md` for detailed instructions.
