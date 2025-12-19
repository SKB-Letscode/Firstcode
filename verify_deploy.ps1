# Simple Deployment Readiness Check
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Render Deployment Readiness Check" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check required files
Write-Host "Checking Required Files:" -ForegroundColor Yellow
Write-Host ""

$files = @{
    "API Service" = "app\server\api_services.py"
    "Web Interface" = "app\web\index.html"
    "DB Connector" = "app\dbconnector.py"
    "SQLite DB" = "DB\1_ImageDB.sqlite"
    "FAISS Index" = "DB\1_faiss_face_index.bin"
    "Face Metadata" = "DB\1_face_metadata.pkl"
    "Procfile" = "Procfile"
    "Requirements" = "requirements.txt"
    "Render Config" = "render.yaml"
    "Runtime" = "runtime.txt"
}

$allPresent = $true

foreach ($item in $files.GetEnumerator()) {
    if (Test-Path $item.Value) {
        Write-Host "  [OK] $($item.Key)" -ForegroundColor Green
    } else {
        Write-Host "  [MISSING] $($item.Key)" -ForegroundColor Red
        $allPresent = $false
    }
}

Write-Host ""

# Check Images folder
if (Test-Path "Images") {
    $imageCount = (Get-ChildItem -Path "Images" -Recurse -File -ErrorAction SilentlyContinue).Count
    Write-Host "  [OK] Images folder ($imageCount files)" -ForegroundColor Green
} else {
    Write-Host "  [MISSING] Images folder" -ForegroundColor Red
    $allPresent = $false
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan

if ($allPresent) {
    Write-Host "READY TO DEPLOY!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Yellow
    Write-Host "1. Commit and push to GitHub"
    Write-Host "2. Go to https://dashboard.render.com"
    Write-Host "3. Create New Web Service"
    Write-Host "4. Follow DEPLOYMENT_GUIDE.md"
} else {
    Write-Host "NOT READY - Missing files!" -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
