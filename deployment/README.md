# AWS EC2 Deployment Files

This directory contains all the necessary files for deploying the FMF application to AWS EC2.

## 📁 Files Overview

### Documentation
- **`QUICKSTART.md`** - Quick 5-step deployment guide (start here!)
- **`../DEPLOYMENT_AWS_EC2.md`** - Complete detailed deployment documentation

### Configuration Files
- **`fmf-app.service`** - Systemd service file for running the app as a service
- **`nginx-fmf.conf`** - Nginx reverse proxy configuration
- **`.env.template`** - Environment variables template

### Scripts
- **`../deploy_ec2.sh`** - Automated deployment script for Ubuntu EC2 (Linux/Bash)
- **`upload_to_ec2.ps1`** - Upload files from Windows to EC2 (PowerShell)

## 🚀 Quick Start

1. **Read the Quick Start Guide**
   ```bash
   cat QUICKSTART.md
   ```

2. **Upload your application** (from Windows):
   ```powershell
   .\upload_to_ec2.ps1
   ```

3. **Deploy on EC2** (on Ubuntu EC2 instance):
   ```bash
   sudo bash deploy_ec2.sh
   ```

## 📚 File Usage

### fmf-app.service
Copy this file to `/etc/systemd/system/` on your EC2 instance:
```bash
sudo cp fmf-app.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable fmf-app
sudo systemctl start fmf-app
```

### nginx-fmf.conf
Copy this file to Nginx sites-available:
```bash
sudo cp nginx-fmf.conf /etc/nginx/sites-available/fmf-app
sudo ln -s /etc/nginx/sites-available/fmf-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### .env.template
Copy and configure on your EC2 instance:
```bash
cp .env.template /home/ubuntu/fmf-app/.env
nano /home/ubuntu/fmf-app/.env  # Edit with your values
```

### deploy_ec2.sh
Automated deployment (includes all above steps):
```bash
cd /home/ubuntu/fmf-app
sudo bash deploy_ec2.sh
```

### upload_to_ec2.ps1
Upload from Windows to EC2:
```powershell
.\upload_to_ec2.ps1 -KeyPath "C:\path\to\key.pem" -EC2Host "1.2.3.4"
```

## 🔗 Related Files

- **Dockerfile** - Docker deployment (alternative to EC2)
- **requirements.txt** - Python dependencies
- **Procfile** - Heroku/cloud deployment format

## 📖 Deployment Options

1. **Manual Deployment** - Follow DEPLOYMENT_AWS_EC2.md step by step
2. **Automated Deployment** - Use deploy_ec2.sh script
3. **Docker Deployment** - Use Dockerfile (alternative approach)

## 🆘 Need Help?

- Start with: `QUICKSTART.md`
- Detailed guide: `../DEPLOYMENT_AWS_EC2.md`
- Common issues covered in both documents

## 📝 Notes

- All scripts assume Ubuntu 22.04 LTS
- Adjust paths in configuration files as needed
- Never commit `.env` file with real credentials
- See `DEPLOYMENT_AWS_EC2.md` for troubleshooting

---

**Ready to deploy?** Start with `QUICKSTART.md` 🚀
