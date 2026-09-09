# Extreme Heatwave Early Warning & Human Thermal Stress Index Platform
Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host "  Extreme Heatwave Early Warning & Human Thermal Stress Index Platform" -ForegroundColor White
Write-Host "  Civic Decision Support & Surveillance System" -ForegroundColor White
Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[*] Checking Python environment..." -ForegroundColor Yellow
$pyVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Python is not installed or not in PATH." -ForegroundColor Red
    pause
    exit 1
}
Write-Host "  Found: $pyVersion" -ForegroundColor Green

Write-Host "[*] Checking and installing dependencies..." -ForegroundColor Yellow
python -m pip install -r requirements.txt

Write-Host "[*] Executing Physics & Formula Tests..." -ForegroundColor Yellow
python test_engine.py

Write-Host "[*] Executing REST API Integration Tests..." -ForegroundColor Yellow
python test_api.py

Write-Host ""
Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host "  Starting Platform Server..." -ForegroundColor Green
Write-Host "  Open your browser to: http://127.0.0.1:8000" -ForegroundColor White
Write-Host "===================================================================" -ForegroundColor Cyan
Write-Host ""

python app.py
