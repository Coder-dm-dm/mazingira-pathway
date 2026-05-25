import requests
from requests.auth import HTTPBasicAuth
from services.data_handler import get_subscribers

LOCAL_IP = "127.0.0.1:8080"
USERNAME = "sms"
PASSWORD = "password123"
SEND_URL = f"http://{LOCAL_IP}/message"

def send_sms_direct(phone, message_text):
    """Dispatches a single HTTP payload command transaction over to the Android loop."""
    payload = {
        "textMessage": {"text": message_text},
        "phoneNumbers": [phone]
    }
    try:
        res = requests.post(SEND_URL, json=payload, auth=HTTPBasicAuth(USERNAME, PASSWORD), timeout=5)
        return res.status_code in [200, 201, 202]
    except Exception as e:
        print(f"[SMS NET FAULT] Connection drop targeting {phone}: {e}")
        return False

def broadcast_campaign(message_body, location_filter="ALL"):
    """Function (b): Loops through records and dispatches targeted text streams."""
    # Query database using subscriber utility handler
    subscribers = get_subscribers(location_filter=(None if location_filter == "ALL" else location_filter))
    success_count = 0
    
    print(f"\n[BROADCAST INITIATION] Targeting: {len(subscribers)} contacts in eco-zone: {location_filter}")
    
    for user in subscribers:
        phone = user["phone"]
        location = user["location"]
        
        # Inject current subscriber location details dynamically if wildcard is in text
        personalized_text = message_body.replace("{LOCATION}", location)
        
        if send_sms_direct(phone, personalized_text):
            success_count += 1
            print(f" -> Sent Successfully to {phone}")
            
    return success_count