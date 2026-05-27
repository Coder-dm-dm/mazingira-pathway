import os
import json
import subprocess

# Locate paths relative to this script file configuration location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "data", "database.json")
HISTORY_FILE = os.path.join(BASE_DIR, "data", "history.json")

def execute_adb_cmd(cmd_list, description):
    """Safely executes an adb process task array."""
    try:
        result = subprocess.run(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
        if result.returncode == 0:
            print(f"   ✅ {description}: Done.")
            return True
        else:
            # Silently track errors if package targets differ on specific Android iterations
            print(f"   ℹ️ {description}: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"   ❌ {description} Error: {e}")
        return False

def reset_android_hardware_sms():
    """Wipes active memory caches and tables from the tethered Android handset."""
    print("\n📱 [WIPING ANDROID TELEPHONY STORAGE STACK]")
    print("-" * 60)
    
    # Verify link state baseline parameters first
    try:
        verify = subprocess.run(["adb", "devices"], stdout=subprocess.PIPE, text=True)
        if "device" not in verify.stdout.split("\n")[1]:
            print("❌ ERROR: Your Android handset is not detected by ADB! Please verify your USB wire link.")
            return
    except:
        print("❌ ERROR: ADB binary tools not found in system PATH variables environment.")
        return

    # 1. Kill tasks to prevent caching issues
    execute_adb_cmd(["adb", "shell", "am", "force-stop", "com.google.android.apps.messaging"], "Stopping Android SMS Application process")
    execute_adb_cmd(["adb", "shell", "am", "force-stop", "com.android.providers.telephony"], "Stopping Telephony DB background process")

    # 2. Completely wipe database app storage allocations
    execute_adb_cmd(["adb", "shell", "pm", "clear", "com.android.providers.telephony"], "Clearing Telephony SQLite storage allocations")
    execute_adb_cmd(["adb", "shell", "pm", "clear", "com.google.android.apps.messaging"], "Clearing Google Messaging application app cache")

    # 3. Direct table deletion queries
    execute_adb_cmd(["adb", "shell", "content", "delete", "--uri", "content://sms"], "Executing master delete row cleanup targeting content://sms")
    execute_adb_cmd(["adb", "shell", "content", "delete", "--uri", "content://sms/inbox"], "Executing clear action targeting content://sms/inbox")
    execute_adb_cmd(["adb", "shell", "content", "delete", "--uri", "content://sms/sent"], "Executing clear action targeting content://sms/sent")

def reset_laptop_json_databases():
    """Wipes out local flat file storage profiles back to pristine brackets arrays."""
    print("\n💻 [CLEARING LOCAL LAPTOP DATABASE LOGS]")
    print("-" * 60)
    
    # Clean subscriber database file array records
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "w") as f:
                json.dump([], f)
            print(f"   ✅ Cleared subscriber repository file lists: {DB_FILE}")
        except Exception as e:
            print(f"   ❌ Error modifying subscribers layout array data mapping files: {e}")
    else:
        print("   ℹ️ database.json file was not found. Skipping file clearing.")

    # Clean historical telemetry dispatch logging arrays
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "w") as f:
                json.dump([], f)
            print(f"   ✅ Reset campaign archive logging records: {HISTORY_FILE}")
        except Exception as e:
            print(f"   ❌ Error resetting history logging configuration parameters: {e}")
    else:
        print("   ℹ️ history.json log array file was not found. Skipping file clearing.")

if __name__ == "__main__":
    print("=" * 60)
    print("⚡ MAZINGIRA DEMO GATEWAY SYSTEM: FULL FACTORY RESET CONTROL SEQUENCE")
    print("=" * 60)
    
    # Process both layers to protect system from sending unintended duplicate alerts
    reset_android_hardware_sms()
    reset_laptop_json_databases()
    
    print("\n✨ SYSTEM COMPLETED CLEAN REBOOT PROFILE TASK ROUTINES. Ready for presentations!")
    print("=" * 60)