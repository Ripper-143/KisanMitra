# KisanMitra Backend Runner and Public Exposer
# This script builds the backend Docker container, runs it locally, and exposes it publicly.

$ErrorActionPreference = "SilentlyContinue"

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "   KisanMitra Docker Backend Deployer        " -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# 1. Build Docker image
Write-Host "`n[1/3] Building Docker image for KisanMitra backend..." -ForegroundColor Yellow
docker build -t kisanmitra-backend ./backend
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Docker build failed. Make sure Docker Desktop is running." -ForegroundColor Red
    exit 1
}

# 2. Run Docker container
Write-Host "`n[2/3] Starting backend container on port 8000..." -ForegroundColor Yellow
docker stop kisanmitra-backend-instance > $null 2>&1
docker rm kisanmitra-backend-instance > $null 2>&1
docker run -d -p 8000:8000 --name kisanmitra-backend-instance kisanmitra-backend
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to start Docker container." -ForegroundColor Red
    exit 1
}

# 3. Check health locally first
Write-Host "Checking local container health..." -ForegroundColor Yellow
Start-Sleep -Seconds 3
$response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
if ($response.status -eq "healthy") {
    Write-Host "Success: Local container started and is healthy!" -ForegroundColor Green
} else {
    Write-Host "Warning: Container started but failed local health check." -ForegroundColor LightRed
}

# 4. Expose via localtunnel
Write-Host "`n[3/3] Exposing port 8000 to the public internet using localtunnel..." -ForegroundColor Yellow
Write-Host "--------------------------------------------------------" -ForegroundColor Green
Write-Host "1. Copy the public URL generated below (e.g., https://xxxx.loca.lt)" -ForegroundColor Green
Write-Host "2. Go to Vercel Settings > Environment Variables" -ForegroundColor Green
Write-Host "3. Set VITE_API_URL to this URL" -ForegroundColor Green
Write-Host "4. Redeploy your frontend on Vercel" -ForegroundColor Green
Write-Host "--------------------------------------------------------`n" -ForegroundColor Green

npx localtunnel --port 8000
