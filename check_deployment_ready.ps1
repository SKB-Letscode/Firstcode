# Pre-Deployment Verification Script for Windows
# Run this before deploying to Render

Write-Host "Checking Render Deployment Readiness..." -ForegroundColor Cyan
Write-Host ""

$allGood = $true

# Check Python version
Write-Host "📌 Checking Python version..." -ForegroundColor Yellow
python --version
Write-Host ""

# Check required files
Write-Host "📁 Checking required files..." -ForegroundColor Yellow

$requiredFiles = @(
    "app\server\api_services.py",
    "app\web\index.html",
    "app\dbconnector.py",
    "DB\1_ImageDB.sqlite",
    "DB\1_faiss_face_index.bin",
    "DB\1_face_metadata.pkl",
    "Procfile",
    "requirements.txt",
    "render.yaml",
    "runtime.txt"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $file NOT FOUND" -ForegroundColor Red
        $allGood = $false
    }
}

# Check Images folder
if (Test-Path "Images") {
    Write-Host "  ✅ Images folder" -ForegroundColor Green
    $imageCount = (Get-ChildItem -Path "Images" -Recurse -File).Count
    Write-Host "     Found $imageCount files in Images folder" -ForegroundColor Gray
} else {
    Write-Host "  ❌ Images folder NOT FOUND" -ForegroundColor Red
    $allGood = $false
}

Write-Host ""

# Check git status
Write-Host "📦 Checking Git status..." -ForegroundColor Yellow
try {
    $gitStatus = git status --porcelain
    if ($gitStatus) {
        Write-Host "  ⚠️  You have uncommitted changes:" -ForegroundColor Yellow
        git status --short
        Write-Host ""
        Write-Host "  Run these commands to commit:" -ForegroundColor Cyan
        Write-Host "  git add ." -ForegroundColor White
        Write-Host "  git commit -m 'Ready for Render deployment'" -ForegroundColor White
        Write-Host "  git push origin master" -ForegroundColor White
    } else {
        Write-Host "  ✅ All changes committed" -ForegroundColor Green
    }
} catch {
    Write-Host "  ℹ️  Not a git repository or git not installed" -ForegroundColor Gray
}

Write-Host ""

# Check API URL in index.html
Write-Host "🌐 Checking API configuration..." -ForegroundColor Yellow
$indexContent = Get-Content "app\web\index.html" -Raw
if ($indexContent -match 'const API_BASE = ''([^'']+)''') {
    $apiUrl = $matches[1]
    Write-Host "  Current API_BASE: $apiUrl" -ForegroundColor White
    if ($apiUrl -eq "http://localhost:8000") {
        Write-Host "  ⚠️  Using localhost - Remember to update after first deployment!" -ForegroundColor Yellow
    }
}

Write-Host ""

# Summary
if ($allGood) {
    Write-Host "✅ All required files are present!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🚀 Next Steps:" -ForegroundColor Cyan
    Write-Host "  1. Make sure all changes are committed and pushed to GitHub" -ForegroundColor White
    Write-Host "  2. Go to https://dashboard.render.com" -ForegroundColor White
    Write-Host "  3. Create a new Web Service" -ForegroundColor White
    Write-Host "  4. Connect your GitHub repository" -ForegroundColor White
    Write-Host "  5. Follow the DEPLOYMENT_GUIDE.md for detailed steps" -ForegroundColor White
    Write-Host ""
    Write-Host "📖 Full guide: DEPLOYMENT_GUIDE.md" -ForegroundColor Cyan
} else {
    Write-Host "❌ Some required files are missing!" -ForegroundColor Red
    Write-Host "   Please ensure all files are present before deploying." -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
