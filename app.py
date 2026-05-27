import os
import subprocess
import threading
import time
import re
from datetime import datetime # Crucial: Used to pull system timestamps for logging
from flask import Flask, render_template, request, redirect, url_for, jsonify

from services.data_handler import save_subscriber, save_manual_subscriber, get_subscribers
from services.history_handler import log_broadcast, get_broadcast_history
from services.ai_handler import generate_ai_broadcast
from services.sms_sender import broadcast_campaign

app = Flask(__name__)

def adb_sms_polling_worker():
    """
    Background worker loop that polls the connected Android device's SMS inbox 
    directly over ADB and prints explicit timestamped authorization records.
    """
    print("[ADB ENGINE] Air-gapped Inbound SMS Daemon activated successfully!")
    
    # Regular expression pattern matching rows from the Android content provider stream
    sms_pattern = re.compile(r"_id=(\d+),\s*address=([^,]+),\s*body=(.*)$")

    while True:
        try:
            # Query the phone's internal SQLite database via ADB bridge
            cmd = ["adb", "shell", "content", "query", "--uri", "content://sms/inbox", "--projection", "_id,address,body"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=4)
            
            if result.returncode == 0 and result.stdout.strip():
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if not line.startswith("Row:"):
                        continue
                        
                    match = sms_pattern.search(line)
                    if match:
                        msg_id = match.group(1).strip()
                        sender_phone = match.group(2).strip()
                        message_body = match.group(3).strip()
                        
                        clean_msg = message_body.upper()
                        if clean_msg.startswith("JOIN"):
                            parts = clean_msg.split(" ", 1)
                            location_zone = parts[1].strip() if len(parts) > 1 else "UNKNOWN"
                            
                            # save_subscriber returns True only if the subscriber is new and successfully recorded
                            if save_subscriber(sender_phone, location_zone):
                                timestamp = datetime.now().strftime("%d/%b/%Y %H:%M:%S")
                                print(f"📢 [{timestamp}] [CONSENT GRANTED] New database entry via inbound text: "
                                      f"\"{message_body}\" from sender {sender_phone} assigned to Zone [{location_zone}].")
                                    
        except subprocess.TimeoutExpired:
            pass # Handle busy link lines gracefully
        except Exception as e:
            print(f"[ADB WORKER FAULT] Exception occurred during phone scan sequence: {e}")
            
        time.sleep(5) # Evaluates the mobile inbox state every 5 seconds

@app.route("/", methods=["GET"])
def index():
    """Renders the central monitoring control panel with live data."""
    subscribers = get_subscribers()
    history = get_broadcast_history()
    
    user_prompt = request.args.get("user_prompt", "")
    generated_text = request.args.get("generated_text", "")
    success_msg = request.args.get("success_msg", "")

    return render_template(
        "index.html",
        registered_numbers=subscribers,
        past_broadcasts=history,
        user_prompt=user_prompt,
        generated_text=generated_text,
        success_msg=success_msg
    )

@app.route("/generate-alert", methods=["POST"])
def generate_alert():
    """Handles the Dual-Mode Inference execution loop sequence."""
    user_prompt = request.form.get("prompt", "").strip()
    generated_text = ""
    
    if user_prompt:
        generated_text = generate_ai_broadcast(user_prompt)
        
    return redirect(url_for("index", user_prompt=user_prompt, generated_text=generated_text))

@app.route("/manual-onboard", methods=["POST"])
def manual_onboard():
    """Manually registers field residents with full physical consent logs."""
    phone = request.form.get("phone", "").strip()
    location = request.form.get("location", "").strip().upper()
    initiative_id = request.form.get("initiative_id", "").strip().upper()
    
    if not phone or not initiative_id:
        return redirect(url_for("index", success_msg="❌ Error: All manual onboarding fields are required."))
        
    saved = save_manual_subscriber(phone, location, initiative_id)
    
    if saved:
        msg = f"🎯 Registered local resident {phone} to [{location}] via initiative link [{initiative_id}]."
    else:
        msg = f"⚠️ Entry Omitted: Subscriber {phone} already exists in records."
        
    return redirect(url_for("index", success_msg=msg))

@app.route("/clear-phone-logs", methods=["POST"])
def clear_phone_logs():
    """Triggers a programmatic ADB cache purge to optimize gateway device space."""
    try:
        subprocess.run(["adb", "shell", "pm", "clear", "com.android.providers.telephony"], check=True)
        msg = "🧹 Success: Handset message logs and caches wiped clean over ADB link loop connection."
    except Exception as e:
        msg = f"⚠️ Housekeeping bypassed: Device was busy or required system authorization root parameters: {e}"
        
    return redirect(url_for("index", success_msg=msg))

@app.route("/send-broadcast", methods=["POST"])
def send_broadcast():
    """Fires the cellular broadcast sequence over the direct USB ADB link interface."""
    message_text = request.form.get("message_text", "").strip()
    target_zone = request.form.get("target_zone", "ALL").strip()
    
    if not message_text:
        return redirect(url_for("index", success_msg="❌ Error: Cannot broadcast an empty message."))

    sent_count = broadcast_campaign(message_text, location_filter=target_zone)
    
    if sent_count > 0:
        log_broadcast(message_text, target_zone)
        msg = f"🎉 Success: Dispatched air-gapped broadcast to {sent_count} device(s) in zone [{target_zone}]."
    else:
        msg = "⚠️ Broadcast completed: 0 active subscribers matched the targeted region sector."

    return redirect(url_for("index", success_msg=msg))

if __name__ == "__main__":
    # Launch the ADB listener daemon worker on a separate thread before firing Flask up
    polling_thread = threading.Thread(target=adb_sms_polling_worker, daemon=True)
    polling_thread.start()
    
    app.run(debug=True, host="0.0.0.0", port=5001, use_reloader=False)