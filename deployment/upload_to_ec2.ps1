# ============================================
# FMF App - Windows Upload Script
# ============================================
# Description: Upload application to EC2 from Windows
# Usage: .\upload_to_ec2.ps1
# ============================================

param(
    [Parameter(Mandatory=$false)]
    [string]$KeyPath,
    
    [Parameter(Mandatory=$false)]
    [string]$EC2Host,
    
    [Parameter(Mandatory=$false)]
    [string]$AppPath = "C:\Work\FMF"
)

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "FMF Application Upload to EC2" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Get SSH key path if not provided
if (-not $KeyPath) {
    $KeyPath = Read-Host "Enter path to your SSH key (.pem file)"
}

# Validate key file exists
if (-not (Test-Path $KeyPath)) {
    Write-Host "[ERROR] SSH key file not found: $KeyPath" -ForegroundColor Red
    exit 1
}

# Get EC2 host if not provided
if (-not $EC2Host) {
    $EC2Host = Read-Host "Enter EC2 public IP or hostname"
}

Write-Host "[INFO] Key Path: $KeyPath" -ForegroundColor Green
Write-Host "[INFO] EC2 Host: $EC2Host" -ForegroundColor Green
Write-Host "[INFO] App Path: $AppPath" -ForegroundColor Green
Write-Host ""

# Check if scp is available
try {
    $null = Get-Command scp -ErrorAction Stop
} catch {
    Write-Host "[ERROR] scp command not found. Please install OpenSSH Client." -ForegroundColor Red
    Write-Host "Install from: Settings > Apps > Optional Features > Add OpenSSH Client" -ForegroundColor Yellow
    exit 1
}

# Confirm upload
Write-Host "Ready to upload application to EC2..." -ForegroundColor Yellow
$confirm = Read-Host "Continue? (Y/N)"
if ($confirm -ne 'Y' -and $confirm -ne 'y') {
    Write-Host "Upload cancelled." -ForegroundColor Yellow
    exit 0
}

Write-Host ""

# Test SSH connectivity first
Write-Host "[INFO] Testing SSH connection..." -ForegroundColor Green
Write-Host "Trying to connect to: ubuntu@$EC2Host" -ForegroundColor Gray

$sshTestCmd = "ssh -i `"$KeyPath`" -o ConnectTimeout=10 -o StrictHostKeyChecking=no ubuntu@$EC2Host `"echo 'Connection successful'`""
Write-Host "Command: $sshTestCmd" -ForegroundColor Gray

try {
    $testResult = Invoke-Expression $sshTestCmd 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "[ERROR] Cannot connect to EC2 instance!" -ForegroundColor Red
        Write-Host "Error details: $testResult" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Common issues:" -ForegroundColor Yellow
        Write-Host "1. Security Group doesn't allow SSH (port 22) from your IP" -ForegroundColor White
        Write-Host "2. EC2 instance is not running or IP address is wrong" -ForegroundColor White
        Write-Host "3. PEM key file doesn't match the instance" -ForegroundColor White
        Write-Host "4. Windows firewall blocking outbound SSH" -ForegroundColor White
        Write-Host ""
        Write-Host "To fix Security Group:" -ForegroundColor Cyan
        Write-Host "  AWS Console > EC2 > Security Groups > Your SG > Inbound Rules" -ForegroundColor Gray
        Write-Host "  Add rule: SSH (22) from My IP" -ForegroundColor Gray
        exit 1
    }
    Write-Host "[SUCCESS] SSH connection test passed!" -ForegroundColor Green
} catch {
    Write-Host ""
    Write-Host "[ERROR] SSH connection failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[INFO] Uploading files to EC2..." -ForegroundColor Green
Write-Host "This may take several minutes depending on your connection speed..." -ForegroundColor Yellow
Write-Host ""

# Create remote directory first
Write-Host "[INFO] Creating remote directory..." -ForegroundColor Green
ssh -i "$KeyPath" -o ConnectTimeout=30 -o StrictHostKeyChecking=no ubuntu@$EC2Host "mkdir -p /home/ubuntu/fmf-app"

# Upload files using scp (recursive)
try {
    # Exclude unnecessary files/folders
    $excludeFiles = @(
        '.git',
        '.vscode',
        '__pycache__',
        '*.pyc',
        '.env',
        'venv',
        'node_modules'
    )
    
    Write-Host "[INFO] Uploading application files..." -ForegroundColor Green
    
    # Use SCP with timeout and connection options
    Write-Host "Starting upload (this may take 5-10 minutes)..." -ForegroundColor Yellow
    
    # SCP with connection timeout and keep-alive
    $scpCmd = "scp -i `"$KeyPath`" -o ConnectTimeout=30 -o ServerAliveInterval=60 -o StrictHostKeyChecking=no -r `"$AppPath`" ubuntu@${EC2Host}:/home/ubuntu/"
    Write-Host "Command: $scpCmd" -ForegroundColor Gray
    
    Invoke-Expression $scpCmd
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "[SUCCESS] Files uploaded successfully!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "[ERROR] Upload failed with exit code: $LASTEXITCODE" -ForegroundColor Red
        exit 1
    }
    
} catch {
    Write-Host ""
    Write-Host "[ERROR] Upload failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Upload Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Connect to EC2:" -ForegroundColor White
Write-Host "   ssh -i $KeyPath ubuntu@$EC2Host" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Run deployment script:" -ForegroundColor White
Write-Host "   cd /home/ubuntu/fmf-app" -ForegroundColor Gray
Write-Host "   sudo bash deploy_ec2.sh" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Configure environment:" -ForegroundColor White
Write-Host "   sudo nano /home/ubuntu/fmf-app/.env" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Access your app:" -ForegroundColor White
Write-Host "   http://$EC2Host" -ForegroundColor Gray
Write-Host ""
Write-Host "For detailed instructions, see DEPLOYMENT_AWS_EC2.md" -ForegroundColor Cyan
Write-Host ""
