#!/usr/bin/env bash

# Climalink Unix/Linux Master Bootstrap Script
echo "=========================================================="
echo "🌱 Initializing Climalink Core Engine & Hardware Bridge..."
echo "=========================================================="

# Ensure execution from the directory containing this script
BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$BASE_DIR"

# 1. Verify Core Interpreter Presence
if ! command -v python3 &> /dev/null; then
    echo "❌ [FATAL ERROR] Python 3 is not installed on this system."
    exit 1
fi

# 2. Virtual Environment Lifecycle Controller
if [ ! -d ".venv" ]; then
    echo "[SYSTEM] Local virtual environment (.venv) not found. Provisioning clean sandbox..."
    python3 -m venv .venv
fi

echo "[SYSTEM] Activating local Python sandbox (.venv)..."
source .venv/bin/activate

# 3. Dynamic Dependency Syncing via requirements.txt
if [ -f "requirements.txt" ]; then
    echo "[SYSTEM] Auditing production dependencies against requirements.txt..."
    pip install --upgrade pip --quiet
    pip install -r requirements.txt --quiet
else
    echo "⚠️  [WARNING] requirements.txt not discovered. Skipping automated package auditing."
fi

# 4. Hardware Bridge Automation & Port Tunneling (ADB)
if command -v adb &> /dev/null; then
    echo "[HARDWARE] Cycle-resetting Android Debug Bridge (ADB) daemon..."
    adb kill-server &> /dev/null
    adb start-server &> /dev/null
    
    # Evaluate device presence loop
    DEVICES_CONNECTED=$(adb devices | grep -v "List of devices" | grep "device" | wc -l | tr -d ' ')
    
    if [ "$DEVICES_CONNECTED" -eq 0 ]; then
        echo "⚠️  [HARDWARE WARNING] No physical USB Android handsets detected via ADB."
        echo "    -> Action Required: Connect phone via USB, enable USB Debugging, and authorize keys."
    else
        echo "[SUCCESS] Active Android node confirmed ($DEVICES_CONNECTED device detected)."
        echo "[HARDWARE] Mapping local TCP port 8080 to Android handset runtime listener..."
        adb forward tcp:8080 tcp:8080
    fi
else
    echo "❌ [ENVIRONMENT ERROR] 'adb' utility not found. Install it using:"
    echo "   Linux: sudo apt install android-tools-adb"
    echo "   macOS: brew install android-platform-tools"
fi

# 5. Core Model Pre-Flight Health Check
if [ ! -f "models/smollm2-135m-instruct-q8_0.gguf" ]; then
    echo "⚠️  [AI ENGINE WARNING] Local GGUF weights missing in 'models/' subdirectory."
    echo "    Air-gapped offline inference fallback mode will experience failure states."
fi

# 6. Execute Application Launch
echo "=========================================================="
echo "🚀 Climalink Interface Live at: http://127.0.0.1:5000"
echo "=========================================================="
python3 app.py