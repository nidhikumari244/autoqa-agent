# AutoQA One-Click Local Launcher
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Launching AutoQA Multi-Modal Platform  " -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

$backendDir = Join-Path $PSScriptRoot "backend"
$frontendDir = Join-Path $PSScriptRoot "frontend"

Write-Host "`n[1/2] Starting FastAPI Backend on http://localhost:8000..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendDir'; .\.venv\Scripts\activate; python run.py"

Start-Sleep -Seconds 2

Write-Host "`n[2/2] Starting Next.js Frontend on http://localhost:3000..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendDir'; npm run dev"

Write-Host "`nAutoQA is booting up!" -ForegroundColor Yellow
Write-Host "• Frontend UI: http://localhost:3000"
Write-Host "• Backend Docs: http://localhost:8000/docs"
Write-Host "=========================================" -ForegroundColor Cyan
