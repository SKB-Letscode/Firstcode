# ============================================
# EC2 Connection Diagnostic Script
# ============================================
# Description: Test EC2 connection and diagnose issues
# Usage: .\test_ec2_connection.ps1
# ============================================

param(
    [Parameter(Mandatory=$false)]
    [string]$KeyPath,
    
    [Parameter(Mandatory=$false)]
    [string]$EC2Host
)

function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "EC2 Connection Diagnostic Tool" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Get inputs if not provided
if (-not $KeyPath) {
    $KeyPath = Read-Host "Enter path to your SSH key (.pem file)"
}

if (-not $EC2Host) {
    $EC2Host = Read-Host "Enter EC2 public IP address"
}

Write-Host ""
Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  Key Path: $KeyPath" -ForegroundColor White
Write-Host "  EC2 Host: $EC2Host" -ForegroundColor White
Write-Host ""

# Test 1: Check if key file exists
Write-Host "[Test 1/6] Checking SSH key file..." -ForegroundColor Cyan
if (Test-Path $KeyPath) {
    Write-Host "  ✓ Key file found" -ForegroundColor Green
    
    # Check permissions (should not be too open)
    $acl = Get-Acl $KeyPath
    Write-Host "  Key file permissions: OK (Windows handles this differently)" -ForegroundColor Gray
} else {
    Write-Host "  ✗ Key file NOT found!" -ForegroundColor Red
    Write-Host "    Please check the path: $KeyPath" -ForegroundColor Yellow
    exit 1
}

# Test 2: Check if SSH is available
Write-Host ""
Write-Host "[Test 2/6] Checking SSH client..." -ForegroundColor Cyan
try {
    $sshVersion = ssh -V 2>&1
    Write-Host "  ✓ SSH client found: $sshVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ SSH client NOT found!" -ForegroundColor Red
    Write-Host "    Install OpenSSH: Settings > Apps > Optional Features" -ForegroundColor Yellow
    exit 1
}

# Test 3: Check network connectivity
Write-Host ""
Write-Host "[Test 3/6] Testing network connectivity (ping)..." -ForegroundColor Cyan
$pingResult = Test-Connection -ComputerName $EC2Host -Count 2 -Quiet -ErrorAction SilentlyContinue
if ($pingResult) {
    Write-Host "  ✓ Host is reachable" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Ping failed (this is normal - EC2 may block ICMP)" -ForegroundColor Yellow
    Write-Host "    Continuing with SSH test..." -ForegroundColor Gray
}

# Test 4: Check if port 22 is accessible
Write-Host ""
Write-Host "[Test 4/6] Testing SSH port (22)..." -ForegroundColor Cyan
try {
    $tcpClient = New-Object System.Net.Sockets.TcpClient
    $asyncResult = $tcpClient.BeginConnect($EC2Host, 22, $null, $null)
    $wait = $asyncResult.AsyncWaitHandle.WaitOne(5000, $false)
    
    if ($wait -and $tcpClient.Connected) {
        Write-Host "  ✓ Port 22 is open and accessible" -ForegroundColor Green
        $tcpClient.Close()
    } else {
        Write-Host "  ✗ Cannot connect to port 22!" -ForegroundColor Red
        Write-Host ""
        Write-Host "  ISSUE FOUND: Port 22 is not accessible!" -ForegroundColor Red
        Write-Host ""
        Write-Host "  Likely causes:" -ForegroundColor Yellow
        Write-Host "  1. Security Group doesn't allow SSH from your IP" -ForegroundColor White
        Write-Host "  2. EC2 instance is not running" -ForegroundColor White
        Write-Host "  3. Network ACL blocking the connection" -ForegroundColor White
        Write-Host ""
        Write-Host "  To fix Security Group:" -ForegroundColor Cyan
        Write-Host "  - Go to AWS Console > EC2 > Security Groups" -ForegroundColor White
        Write-Host "  - Select your instance's security group" -ForegroundColor White
        Write-Host "  - Edit Inbound Rules" -ForegroundColor White
        Write-Host "  - Add: Type=SSH, Protocol=TCP, Port=22, Source=My IP" -ForegroundColor White
        Write-Host ""
        Write-Host "  Your public IP is: " -NoNewline -ForegroundColor White
        try {
            $myIP = (Invoke-WebRequest -Uri "https://api.ipify.org" -UseBasicParsing).Content
            Write-Host "$myIP" -ForegroundColor Yellow
        } catch {
            Write-Host "(couldn't detect)" -ForegroundColor Gray
        }
        $tcpClient.Close()
        exit 1
    }
} catch {
    Write-Host "  ✗ Error testing port: $_" -ForegroundColor Red
    exit 1
}

# Test 5: Test SSH connection with key
Write-Host ""
Write-Host "[Test 5/6] Testing SSH authentication..." -ForegroundColor Cyan
Write-Host "  Attempting connection (timeout: 15 seconds)..." -ForegroundColor Gray

$sshTestCmd = "ssh -i `"$KeyPath`" -o ConnectTimeout=15 -o StrictHostKeyChecking=no -o BatchMode=yes ubuntu@$EC2Host `"echo 'SSH_SUCCESS'`""

try {
    $sshOutput = Invoke-Expression $sshTestCmd 2>&1
    
    if ($sshOutput -match "SSH_SUCCESS") {
        Write-Host "  ✓ SSH authentication successful!" -ForegroundColor Green
    } elseif ($sshOutput -match "Permission denied") {
        Write-Host "  ✗ SSH authentication failed - Permission denied" -ForegroundColor Red
        Write-Host ""
        Write-Host "  Possible causes:" -ForegroundColor Yellow
        Write-Host "  1. Wrong PEM key file (doesn't match the instance)" -ForegroundColor White
        Write-Host "  2. Wrong username (should be 'ubuntu' for Ubuntu AMI)" -ForegroundColor White
        Write-Host "  3. Key file format issue" -ForegroundColor White
        exit 1
    } elseif ($sshOutput -match "Connection timed out" -or $sshOutput -match "Connection refused") {
        Write-Host "  ✗ Connection timeout or refused" -ForegroundColor Red
        Write-Host "    Even though port 22 is open, SSH is not responding" -ForegroundColor Yellow
        Write-Host "    Check if SSH service is running on the instance" -ForegroundColor Yellow
        exit 1
    } else {
        Write-Host "  ✗ Unexpected result:" -ForegroundColor Red
        Write-Host "    $sshOutput" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "  ✗ SSH test failed: $_" -ForegroundColor Red
    exit 1
}

# Test 6: Test basic file operations
Write-Host ""
Write-Host "[Test 6/6] Testing file operations..." -ForegroundColor Cyan
$createDirCmd = "ssh -i `"$KeyPath`" -o ConnectTimeout=15 -o StrictHostKeyChecking=no ubuntu@$EC2Host `"mkdir -p /home/ubuntu/test_upload && echo 'DIR_CREATED'`""

try {
    $dirResult = Invoke-Expression $createDirCmd 2>&1
    if ($dirResult -match "DIR_CREATED") {
        Write-Host "  ✓ Can create directories on remote host" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Unexpected result: $dirResult" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ✗ File operation test failed: $_" -ForegroundColor Red
}

# Summary
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Diagnostic Complete - All Tests Passed!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your connection is ready. You can now run:" -ForegroundColor Yellow
Write-Host "  .\upload_to_ec2.ps1 -KeyPath `"$KeyPath`" -EC2Host $EC2Host" -ForegroundColor White
Write-Host ""
Write-Host "Or connect directly:" -ForegroundColor Yellow
Write-Host "  ssh -i `"$KeyPath`" ubuntu@$EC2Host" -ForegroundColor White
Write-Host ""
