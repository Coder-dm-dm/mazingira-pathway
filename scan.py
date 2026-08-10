import requests
from requests.auth import HTTPBasicAuth

LOCAL_IP = "192.168.1.99:8080"
USERNAME = "sms"
PASSWORD = "password123"

# Every possible path variation this specific gateway app framework uses
paths_to_test = [
    "/message",
    "/messages",
    "/v1/message",
    "/v1/messages",
    "/api/message",
    "/api/messages",
    "/api/v1/message",
    "/api/v1/messages"
]

print("🔍 SCANNING TABLET SERVER FOR VALID PATHS...")
print("=" * 50)

for path in paths_to_test:
    url = f"http://{LOCAL_IP}{path}"
    try:
        # Sending a blank post request just to check the path response code
        response = requests.post(url, json={}, auth=HTTPBasicAuth(USERNAME, PASSWORD), timeout=3)
        
        # If it returns a 400 or 422, the path exists! It's just complaining about the empty JSON.
        if response.status_code in [200, 201, 202]:
            print(f"🎯 MATCH FOUND! Path: {path} -> SUCCESS ({response.status_code})")
        elif response.status_code in [400, 422]:
            print(f"✅ PATH EXISTS! Path: {path} -> Server responded with {response.status_code} (Valid path structure!)")
        else:
            print(f"❌ NOT FOUND: Path: {path} -> Status {response.status_code}")
            
    except Exception as e:
        print(f"💥 Connection Error on {path}: {e}")

print("=" * 50)
print("Scan complete.")