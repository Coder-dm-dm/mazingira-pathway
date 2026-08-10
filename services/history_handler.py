import os
import json
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")

def _init_history():
    """Ensures file structures exist on the local workspace node."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "w") as f:
            json.dump([], f)

def get_broadcast_history():
    """Function (d): Retrieves history records sorted by latest entry first."""
    _init_history()
    try:
        with open(HISTORY_FILE, "r") as f:
            logs = json.load(f)
        return sorted(logs, key=lambda x: x["time"], reverse=True)
    except Exception as e:
        print(f"[LOG ERROR] Parsing execution failure: {e}")
        return []

def log_broadcast(message_text, target_zone):
    """Function (d): Commits a completed campaign run to local system history files."""
    _init_history()
    logs = get_broadcast_history()
    
    new_entry = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "zone": target_zone.upper(),
        "message": message_text
    }
    
    logs.append(new_entry)
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(logs, f, indent=4)
    except Exception as e:
        print(f"[LOG ERROR] Appending operation aborted: {e}")