import time
import subprocess
import json
import requests
from requests.auth import HTTPBasicAuth

# 1. Exact Network parameters pulled from your active screen layouts
LOCAL_IP = "192.168.1.99:8080"
USERNAME = "sms"
PASSWORD = "password123"

SEND_URL = f"http://{LOCAL_IP}/v1/sms/send"

def get_inbound_sms_via_adb():
    """Queries Android internal telephony data provider directly via ADB."""
    try:
        # Command querying system inbox table sorting by descending date ID
        cmd = "adb shell content query --uri content://sms/inbox --projection address,body"
        
        # Execute the shell line safely inside Python subprocess
        result = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL).decode('utf-8', errors='ignore')
        
        parsed_messages = []
        for line in result.strip().split('\n'):
            if "address=" in line and "body=" in line:
                # Basic string parsing extracting information segments from raw console lines
                # Format expected: Row: 0 address=+2547..., body=JOIN NAIROBI
                parts = line.split("address=")
                if len(parts) > 1:
                    sub_parts = parts[1].split(", body=")
                    if len(sub_parts) > 1:
                        sender = sub_parts[0].strip()
                        body = sub_parts[1].strip()
                        parsed_messages.append({"sender": sender, "text": body})
                        
        return parsed_messages
    except Exception:
        # If wireless ADB falls asleep momentarily, handle smoothly without crashing script
        return []

def check_and_process_registrations():
    # Fetch real-time system strings over the ADB wire
    messages = get_inbound_sms_via_adb()
    
    for msg in messages:
        sender = msg['sender']
        text = msg['text'].strip().upper()
        
        if "JOIN" in text:
            # Parse target locations
            parts = text.split(" ")
            location = parts[1] if len(parts) > 1 else "KENYA"
            
            if not is_already_registered(sender):
                # Append verified subscriber metadata inside text flat file storage
                with open("database.txt", "a") as db:
                    db.write(f"{sender},{location}\n")
                print(f"\n[REGISTRATION LIVE] Added subscriber {sender} targeting zone: {location}")
                
                # Command the functioning tablet application to fire confirmation SMS back out
                confirmation_msg = f"Mazingira Alert: Confirmed! Registered for resilience updates in {location}."
                send_sms(sender, confirmation_msg)
            else:
                # Do nothing if subscriber is already tracked to protect bundle resources
                pass

def is_already_registered(phone_number):
    try:
        with open("database.txt", "r") as db:
            return phone_number in db.read()
    except FileNotFoundError:
        return False

def send_sms(phone_number, message_text):
    # Formats payload structure mapping to SMSGate specification standards
    payload = {
        "phone": phone_number,
        "message": message_text
    }
    try:
        response = requests.post(
            SEND_URL, 
            json=payload, 
            auth=HTTPBasicAuth(USERNAME, PASSWORD), 
            timeout=5
        )
        if response.status_code in [200, 201]:
            print(f"[OUTBOUND SUCCESS] Fired reply tracking back to sender: {phone_number}")
        else:
            print(f"[OUTBOUND ERROR] Server rejected payload request: {response.status_code}")
    except Exception as e:
        print(f"[PIPELINE FAULT] Failed to complete REST command: {e}")

# Main execution frame block
print("="*60)
print("MAZINGIRA ECO-SYSTEM HYBRID GATEWAY OPERATIONAL")
print(f"Reading Inbound Threads via: Native ADB shell query")
print(f"Dispatching Outbound Traffic via: http://{LOCAL_IP}")
print("System listening cycles online. Press Ctrl+C to terminate loops.")
print("="*60)

while True:
    check_and_process_registrations()
    time.sleep(3) # Iterate collection routine loops every 3 seconds