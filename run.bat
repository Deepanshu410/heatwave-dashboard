@echo off
title Extreme Heatwave Early Warning & Human Thermal Stress Index Platform
color 0A

echo ===================================================================
echo   Extreme Heatwave Early Warning & Human Thermal Stress Index Platform
echo   Bioclimatic Decision Support & Surveillance System
echo ===================================================================
echo.

echo [*] Checking Python environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH. Please install Python 3.9+.
    pause
    exit /b 1
)

echo [*] Installing dependencies if needed...
python -m pip install -r requirements.txt

echo [*] Executing System Verification Tests...
python test_engine.py
python test_api.py

echo.
echo ===================================================================
echo   Starting Early Warning Platform...
echo   Open your browser and navigate to: http://127.0.0.1:8000
echo ===================================================================
echo.

python app.py
pause
