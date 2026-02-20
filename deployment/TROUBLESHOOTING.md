# EC2 Connection Troubleshooting Guide

## ❌ Common Issue: Connection Timeout

When you see "Connection timed out" or the upload script hangs, it's usually one of these issues:

### 1. Security Group Not Configured Properly ⭐ MOST COMMON

**Symptoms:**
- Script hangs when trying to connect
- "Connection timed out" error
- Port 22 test fails

**Fix:**
1. Go to **AWS Console** → **EC2** → **Instances**
2. Select your instance → **Security** tab
3. Click on the **Security Group** (e.g., `sg-xxxxx`)
4. Click **Edit inbound rules**
5. Add a new rule:
   - **Type**: SSH
   - **Protocol**: TCP
   - **Port**: 22
   - **Source**: My IP (or your specific IP)
6. Click **Save rules**

**Quick test:**
```powershell
# Run the diagnostic script
cd C:\Work\FMF\deployment
.\test_ec2_connection.ps1
```

### 2. Wrong EC2 Instance IP Address

**Symptoms:**
- "No route to host" error
- Ping fails

**Fix:**
1. Go to **AWS Console** → **EC2** → **Instances**
2. Select your instance
3. Copy the **Public IPv4 address** (not private IP!)
4. Verify instance is **Running** (not stopped or terminated)

### 3. SSH Key Mismatch

**Symptoms:**
- "Permission denied (publickey)" error
- Authentication fails even though connection works

**Fix:**
1. Verify you're using the correct `.pem` file that was selected when launching the instance
2. If lost, you cannot recover it - must create a new instance with a new key pair

### 4. Instance Not Running

**Symptoms:**
- Connection timeout
- No response

**Fix:**
1. Go to **AWS Console** → **EC2** → **Instances**
2. Check **Instance State** is **Running**
3. If stopped, select instance → **Instance State** → **Start instance**

### 5. Network ACL Blocking Connection

**Symptoms:**
- Port 22 appears closed even with correct Security Group

**Fix:**
1. Go to **AWS Console** → **VPC** → **Network ACLs**
2. Select the ACL associated with your subnet
3. Check **Inbound Rules** allow port 22
4. Check **Outbound Rules** allow return traffic

### 6. Windows Firewall Blocking Outbound SSH

**Symptoms:**
- Works on other networks but not yours
- Corporate/restricted network

**Fix:**
```powershell
# Test with Windows firewall temporarily disabled
# Or add an outbound rule for SSH
```

Alternatively, contact your network administrator.

---

## 🔧 Diagnostic Tools

### Test #1: Run Diagnostic Script
```powershell
cd C:\Work\FMF\deployment
.\test_ec2_connection.ps1
```
This will check:
- ✓ Key file exists
- ✓ SSH client installed
- ✓ Network connectivity
- ✓ Port 22 accessible
- ✓ SSH authentication works
- ✓ File operations work

### Test #2: Manual Port Check
```powershell
Test-NetConnection -ComputerName YOUR_EC2_IP -Port 22
```
Should show: **TcpTestSucceeded: True**

### Test #3: Manual SSH Test
```powershell
ssh -i "path\to\key.pem" -v ubuntu@YOUR_EC2_IP
```
The `-v` flag shows verbose output for debugging.

### Test #4: Check Your Public IP
```powershell
(Invoke-WebRequest -Uri "https://api.ipify.org").Content
```
Use this IP in your Security Group rule.

---

## ✅ Quick Fix Checklist

Run through this checklist:

- [ ] EC2 instance is **Running**
- [ ] Using the correct **Public IP** address
- [ ] Using the correct **.pem** key file
- [ ] Security Group allows **SSH (port 22)** from your IP
- [ ] Network ACL allows inbound port 22
- [ ] SSH client is installed on Windows
- [ ] Not using VPN or restrictive firewall

---

## 🚀 After Fixing Connection Issues

Once connection is working, upload your app:

```powershell
cd C:\Work\FMF\deployment

# Option 1: With parameters
.\upload_to_ec2.ps1 -KeyPath "C:\path\to\key.pem" -EC2Host "1.2.3.4"

# Option 2: Interactive (will prompt)
.\upload_to_ec2.ps1
```

---

## 📞 Still Having Issues?

1. **Run the diagnostic**: `.\test_ec2_connection.ps1`
2. **Check error message** - it usually tells you exactly what's wrong
3. **Verify Security Group** - this is the #1 cause of connection issues
4. **Try different network** - test from a hotspot to rule out local network issues

---

## 💡 Pro Tips

### Set Correct Key File Permissions (if needed)
Windows handles this automatically, but if you have issues:
```powershell
icacls "your-key.pem" /inheritance:r
icacls "your-key.pem" /grant:r "$($env:USERNAME):(R)"
```

### Save Connection Details
Create a shortcut script:
```powershell
# Create: connect_to_ec2.ps1
$KeyPath = "C:\path\to\your-key.pem"
$EC2Host = "your.ec2.ip.address"
ssh -i $KeyPath ubuntu@$EC2Host
```

### Use Windows Terminal
Better SSH experience:
```powershell
winget install Microsoft.WindowsTerminal
```

---

## 📖 Related Documentation

- [QUICKSTART.md](QUICKSTART.md) - Quick deployment guide
- [DEPLOYMENT_AWS_EC2.md](../DEPLOYMENT_AWS_EC2.md) - Full deployment documentation
- [upload_to_ec2.ps1](upload_to_ec2.ps1) - Upload script
- [test_ec2_connection.ps1](test_ec2_connection.ps1) - Diagnostic script
