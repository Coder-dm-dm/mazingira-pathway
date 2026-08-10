import os
import json

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
DB_FILE = os.path.join(DATA_DIR, "database.json")

def _init_db():
    """Guarantees the storage file system paths exist cleanly on start."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump([], f)

def get_subscribers(location_filter=None):
    """Function (e): Fetches data logs from disk, with optional zone filtering."""
    _init_db()
    try:
        with open(DB_FILE, "r") as f:
            records = json.load(f)
        
        if location_filter:
            return [r for r in records if r["location"].upper() == location_filter.upper()]
        return records
    except Exception as e:
        print(f"[DB ERROR] Read exception occurred: {e}")
        return []

def save_subscriber(phone, location):
    """Function (e): Saves an automated inbound webhook subscriber while safely blocking duplicates."""
    _init_db()
    records = get_subscribers()
    
    # Check for duplicate numbers
    if any(r["phone"] == phone for r in records):
        return False  # Duplicate ignored
        
    records.append({"phone": phone, "location": location.upper(), "initiative_id": "INBOUND_SMS"})
    
    try:
        with open(DB_FILE, "w") as f:
            json.dump(records, f, indent=4)
        return True
    except Exception as e:
        print(f"[DB ERROR] Write processing exception: {e}")
        return False

def save_manual_subscriber(phone, location, initiative_id):
    """Saves a manually entered dashboard resident with explicit initiative tracking."""
    _init_db()
    records = get_subscribers()
    
    # Check for duplicate numbers
    if any(r["phone"] == phone for r in records):
        return False  # Duplicate ignored
        
    records.append({
        "phone": phone, 
        "location": location.upper(), 
        "initiative_id": initiative_id.upper()
    })
    
    try:
        with open(DB_FILE, "w") as f:
            json.dump(records, f, indent=4)
        return True
    except Exception as e:
        print(f"[DB ERROR] Manual write processing exception: {e}")
        return False