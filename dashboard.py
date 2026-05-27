import subprocess
import os
from services.data_handler import get_subscribers, save_subscriber
from services.sms_sender import broadcast_campaign

def clear_phone_storage():
    """Wipes old messages using ADB."""
    print("\n🧹 Clearing phone message cache...")
    subprocess.run(["adb", "shell", "pm", "clear", "com.android.providers.telephony"])
    print("✅ Cache cleared.")

def main_menu():
    while True:
        print("\n=== MAZINGIRA HUB CLI DASHBOARD ===")
        print("1. View Active Subscribers")
        print("2. Manual Registration (Onboard)")
        print("3. Trigger Climate Alert Broadcast")
        print("4. Maintenance: Clear Phone Logs")
        print("0. Exit")
        
        choice = input("\nSelect option: ")
        
        if choice == "1":
            subs = get_subscribers()
            for s in subs:
                print(f"[{s['location']}] {s['phone']}")
        
        elif choice == "2":
            phone = input("Enter phone number: ")
            loc = input("Enter Eco-Zone (e.g. NAKURU): ")
            if save_subscriber(phone, loc):
                print("✅ Subscriber saved.")
            else:
                print("⚠️ Error: Subscriber exists or invalid input.")
                
        elif choice == "3":
            zone = input("Target Zone: ")
            msg = input("Alert Message: ")
            broadcast_campaign(msg, location_filter=zone)
            print("✅ Broadcast command sent to gateway.")
            
        elif choice == "4":
            clear_phone_storage()
            
        elif choice == "0":
            break

if __name__ == "__main__":
    # Ensure ADB is connected before starting
    adb_check = subprocess.run(["adb", "devices"], capture_output=True, text=True)
    if "device" in adb_check.stdout:
        print("🚀 ADB Connected. System Ready.")
        main_menu()
    else:
        print("❌ CRITICAL: No Android device detected via ADB.")