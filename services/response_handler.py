import time
import subprocess
import re
import threading
from datetime import datetime

from services.data_handler import save_subscriber
from services.ai_handler import generate_ai_response

# Shared Anti-Echo Memory Registry
sent_messages_history = set()


def is_valid_phone_number(sender):
    if not sender:
        return False
    clean = sender.strip().replace('+', '')
    return clean.isdigit() and len(clean) >= 8


def normalize_text(text):
    return re.sub(r'\s+', '', text.strip().lower())


def process_inbound_sms(sender_phone, message_body):
    from services.sms_sender import send_sms_direct

    if not is_valid_phone_number(sender_phone):
        return {"status": "ignored_carrier"}

    norm_body = normalize_text(message_body)

    # BLOCK SELF-ECHO LOOPS
    if norm_body in sent_messages_history:
        print(f"🚫 [BLOCKED SELF-ECHO] Ignored loop message from {sender_phone}")
        return {"status": "ignored_echo"}

    sent_messages_history.add(norm_body)

    timestamp = datetime.now().strftime("%d/%b/%Y %H:%M:%S")
    clean_msg = message_body.strip()

    if clean_msg.upper().startswith("JOIN"):
        parts = clean_msg.upper().split(" ", 1)
        location_zone = parts[1].strip() if len(parts) > 1 else "UNKNOWN"
        save_subscriber(sender_phone, location_zone)
        welcome_msg = f"Karibu Climalink! Umesajiliwa katika eneo la {location_zone}. Uliza swali lolote la kilimo."
        
        sent_messages_history.add(normalize_text(welcome_msg))
        send_sms_direct(sender_phone, welcome_msg)
        return {"status": "subscribed"}

    print(f"\n📩 [{timestamp}] [INBOUND QUESTION] From {sender_phone}: \"{message_body}\"")
    ai_reply = generate_ai_response(message_body, phone_number=sender_phone)
    
    sent_messages_history.add(normalize_text(ai_reply))
    dispatched = send_sms_direct(sender_phone, ai_reply)
    
    return {"status": "ai_replied", "reply": ai_reply, "dispatched": dispatched}


def adb_sms_polling_worker():
    print("[ADB ENGINE] Inbound SMS Daemon Active...")
    cmd = ["adb", "shell", "content", "query", "--uri", "content://sms/inbox", "--projection", "_id,address,body"]
    sms_pattern = re.compile(r"_id=(\d+),\s*address=([^,]+),\s*body=(.*)$")
    processed_sms_ids = set()

    # Startup Anti-Echo Pre-fill
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=4)
        if res.returncode == 0 and res.stdout.strip():
            for line in res.stdout.strip().split('\n'):
                if line.startswith("Row:"):
                    m = sms_pattern.search(line)
                    if m:
                        processed_sms_ids.add(m.group(1).strip())
                        sent_messages_history.add(normalize_text(m.group(3).strip()))
        print(f"🔒 [ADB DAEMON] Anti-echo pre-filled with {len(sent_messages_history)} past messages.")
    except Exception as e:
        print(f"⚠️ Pre-fill skipped: {e}")

    while True:
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=4)
            if res.returncode == 0 and res.stdout.strip():
                for line in res.stdout.strip().split('\n'):
                    if line.startswith("Row:"):
                        m = sms_pattern.search(line)
                        if m:
                            msg_id = m.group(1).strip()
                            if msg_id in processed_sms_ids:
                                continue
                            processed_sms_ids.add(msg_id)
                            process_inbound_sms(m.group(2).strip(), m.group(3).strip())
        except Exception:
            pass
        time.sleep(3)


def start_adb_daemon():
    thread = threading.Thread(target=adb_sms_polling_worker, daemon=True)
    thread.start()
    return thread