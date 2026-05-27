@echo off
title Climalink Bootstrapper
echo ==========================================================
echo 🌱 Initializing Climalink Core Engine ^& Hardware Bridge...
echo ==========================================================

:: 1. Verify Python Presence
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ [FATAL ERROR] Python is not installed or not added to System PATH.
    pause
    exit /b 1
)

:: 2. Virtual Environment Lifecycle Controller
if not exist .venv (
    echo [SYSTEM] Local virtual environment ^(.venv^) not found. Provisioning clean sandbox...
    python -m venv .venv
)

echo [SYSTEM] Activating local Python sandbox ^(.venv^)...
call .venv\Scripts\activate

:: 3. Dynamic Dependency Syncing via requirements.txt
if exist requirements.txt (
    echo [SYSTEM] Auditing production dependencies against requirements.txt...
    python -m pip install --upgrade pip --quiet
    pip install -r requirements.txt --quiet
) else (
    echo ⚠️  [WARNING] requirements.txt not discovered. Skipping automated package auditing.
)

:: 4. Hardware Bridge Automation ^& Port Tunneling (ADB)
where adb >nul 2>nul
if %errorlevel% eq 0 (
    echo [HARDWARE] Cycle-resetting Android Debug Bridge ^(ADB^) daemon...
    adb kill-server >nul 2>nul
    adb start-server >nul 2>nul
    
    :: Forward local TCP port 8080 to Android device
    echo [HARDWARE] Mapping local TCP port 8080 to Android handset runtime listener...
    adb forward tcp:8080 tcp:8080
    echo [SUCCESS] ADB Port Forwarding complete. Make sure your USB device is plugged in!
) else (
    echo ❌ [ENVIRONMENT ERROR] 'adb' utility not found. 
    echo    Please download Android Platform Tools and add 'adb' to your Windows Environment Variables.
)

:: 5. Core Model Pre-Flight Health Check
if not exist models\smollm2-135m-instruct-q8_0.gguf (
    echo ⚠️  [AI ENGINE WARNING] Local GGUF weights missing in 'models\' subdirectory.
    echo    Air-gapped offline inference fallback mode will experience failure states.
)

:: 6. Execute Application Launch
echo ==========================================================
echo 🚀 Climalink Interface Live at: http://127.0.0.1:5000
echo ==========================================================
python app.py
pause