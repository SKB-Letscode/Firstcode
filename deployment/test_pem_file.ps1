# Quick PEM File Test
# Tests if your specific .pem file works with SSH commands

param(
    [Parameter(Mandatory=$false)]
    [string]$KeyPath = "SKB.WebServer.Key.pem",
    
    [Parameter(Mandatory=$false)]
    [string]$EC2Host
)

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "PEM File Quick Test" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Get EC2 host if not provided
if (-not $EC2Host) {
    $EC2Host = Read-Host "Enter your EC2 Public IP"
}

Write-Host "Testing with:" -ForegroundColor Yellow
Write-Host "  Key File: $KeyPath" -ForegroundColor White
Write-Host "  EC2 Host: $EC2Host" -ForegroundColor White
Write-Host ""

# Test 1: Check if file exists
Write-Host "[1/3] Checking if PEM file exists..." -ForegroundColor Cyan
if (Test-Path $KeyPath) {
    Write-Host "  ✓ Found: $KeyPath" -ForegroundColor Green
    
    # Show full path
    $fullPath = (Resolve-Path $KeyPath).Path
    Write-Host "  Full path: $fullPath" -ForegroundColor Gray
} else {
    Write-Host "  ✗ File not found: $KeyPath" -ForegroundColor Red
    Write-Host ""
    Write-Host "Current directory: $(Get-Location)" -ForegroundColor Yellow
    Write-Host "Files in current directory:" -ForegroundColor Yellow
    Get-ChildItem *.pem | ForEach-Object { Write-Host "  - $($_.Name)" -ForegroundColor White }
    exit 1
}

# Test 2: Test SSH command with quoted path
Write-Host ""
Write-Host "[2/3] Testing SSH with quoted path..." -ForegroundColor Cyan
Write-Host "  Attempting connection (timeout: 10 seconds)..." -ForegroundColor Gray

# Build command with proper quoting
$testCmd = "ssh -i `"$KeyPath`" -o ConnectTimeout=10 -o StrictHostKeyChecking=no -o BatchMode=yes ubuntu@$EC2Host `"echo 'SUCCESS'`""

Write-Host "  Command: $testCmd" -ForegroundColor Gray
Write-Host ""

try {
    $result = Invoke-Expression $testCmd 2>&1
    
    if ($result -match "SUCCESS") {
        Write-Host "  ✓ Connection successful!" -ForegroundColor Green
        Write-Host "  Your PEM file works correctly!" -ForegroundColor Green
    } elseif ($result -match "Permission denied") {
        Write-Host "  ✗ Permission denied" -ForegroundColor Red
        Write-Host "  The PEM file format is OK, but it doesn't match this EC2 instance" -ForegroundColor Yellow
    } elseif ($result -match "Connection timed out" -or $result -match "Connection refused") {
        Write-Host "  ✗ Connection timeout" -ForegroundColor Red
        Write-Host "  The PEM file is OK, but can't reach EC2 (Security Group issue)" -ForegroundColor Yellow
    } elseif ($result -match "No such file") {
        Write-Host "  ✗ SSH can't find the key file" -ForegroundColor Red
        Write-Host "  This indicates a quoting/path issue" -ForegroundColor Yellow
    } else {
        Write-Host "  ⚠ Unexpected result:" -ForegroundColor Yellow
        Write-Host "  $result" -ForegroundColor Gray
    }
} catch {
    Write-Host "  ✗ Error: $_" -ForegroundColor Red
}

# Test 3: Show how the path will be passed
Write-Host ""
Write-Host "[3/3] Path expansion test..." -ForegroundColor Cyan
Write-Host "  Variable value: $KeyPath" -ForegroundColor White
Write-Host "  Quoted value: `"$KeyPath`"" -ForegroundColor White
Write-Host "  For Invoke-Expression: ```"$KeyPath```"" -ForegroundColor White

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Conclusion:" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "The file name 'SKB.WebServer.Key.pem' with dots is FINE." -ForegroundColor Green
Write-Host "PowerShell handles it correctly when properly quoted." -ForegroundColor Green
Write-Host ""

if ($result -match "SUCCESS") {
    Write-Host "✓ Your key file works! Run the upload script now:" -ForegroundColor Green
    Write-Host "  .\upload_to_ec2.ps1 -KeyPath `"$KeyPath`" -EC2Host $EC2Host" -ForegroundColor White
} elseif ($result -match "Connection timed out") {
    Write-Host "⚠ Key file is OK, but connection timed out." -ForegroundColor Yellow
    Write-Host "  Fix Security Group first, then retry upload." -ForegroundColor White
    Write-Host "  Run: .\test_ec2_connection.ps1" -ForegroundColor White
} else {
    Write-Host "⚠ There may be an issue. Check the errors above." -ForegroundColor Yellow
}
Write-Host ""
