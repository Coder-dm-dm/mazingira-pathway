import os
import requests
from requests.auth import HTTPBasicAuth

# Server configuration matching your tablet's local mode profile
LOCAL_IP = "192.168.1.99:8080"
USERNAME = "sms"
PASSWORD = "password123"
SEND_URL = f"http://{LOCAL_IP}/message"

def read_subscribers_from_database():
    subscribers = []
    if not os.path.exists("database.txt"):
        print("[ERROR] database.txt file not found!")
        return subscribers

    with open("database.txt", "r") as db:
        for line in db:
            if line.strip() and "," in line:
                phone, location = line.strip().split(",", 1)
                subscribers.append({"phone": phone.strip(), "location": location.strip()})
    return subscribers

def broadcast_emergency_alert(custom_message_template):
    subscribers = read_subscribers_from_database()
    
    if not subscribers:
        print("[SYSTEM] Broadcast canceled. No contacts inside database.txt.")
        return

    print(f"\n[STARTING APP BROADCAST] Target queue: {len(subscribers)} contacts found.")
    print(f"[TARGET ENDPOINT] {SEND_URL}")
    print("-" * 50)

    for index, user in enumerate(subscribers, start=1):
        phone_number = user["phone"]
        location = user["location"]
        
        # Inject user location into template
        personalized_message = custom_message_template.replace("{LOCATION}", location)
        
        # Exact JSON Schema for the local CapCom6 Android Gateway Build
        payload = {
            "textMessage": {
                "text": personalized_message
            },
            "phoneNumbers": [phone_number]
        }

        try:
            response = requests.post(
                SEND_URL, 
                json=payload, 
                auth=HTTPBasicAuth(USERNAME, PASSWORD), 
                timeout=5
            )
            
            if response.status_code in [200, 201, 202]:
                print(f"[{index}/{len(subscribers)}] Sent to App Queue ➡️ {phone_number} ({location})")
            else:
                print(f"[{index}/{len(subscribers)}] ❌ Server Rejected. Code: {response.status_code}")
                print(f"Server response text: {response.text}")
                
        except Exception as e:
            print(f"[{index}/{len(subscribers)}] 💥 Network connection drop: {e}")

    print("-" * 50)
    print("[BROADCAST COMPLETED] Check your app dashboard layout.")

if __name__ == "__main__":
    alert_template = "MAZINGIRA UPDATE: Heavy weather alert detected for {LOCATION} zone. Monitor drainage systems."
    broadcast_emergency_alert(alert_template)