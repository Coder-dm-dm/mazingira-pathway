import os
from flask import Flask, render_template, request, redirect, url_for, jsonify

# Import the clean functional engines built by your team
from services.data_handler import save_subscriber, get_subscribers
from services.history_handler import log_broadcast, get_broadcast_history
from services.ai_handler import generate_ai_broadcast
from services.sms_sender import broadcast_campaign

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    """Renders the central monitoring control panel with live data."""
    # Pull current records from local JSON files
    subscribers = get_subscribers()
    history = get_broadcast_history()
    
    # Capture optional tracking arguments passed back from form redirection states
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
    """Handles the Edge AI inference generation sequence."""
    user_prompt = request.form.get("prompt", "").strip()
    generated_text = ""
    
    if user_prompt:
        generated_text = generate_ai_broadcast(user_prompt)
        
    # Redirect back to home route with arguments to keep the text fields populated
    return redirect(url_for("index", user_prompt=user_prompt, generated_text=generated_text))

@app.route("/send-broadcast", methods=["POST"])
def send_broadcast():
    """Fires the cellular broadcast sequence over the local network interface."""
    message_text = request.form.get("message_text", "").strip()
    target_zone = request.form.get("target_zone", "ALL").strip()
    
    if not message_text:
        return redirect(url_for("index", success_msg="❌ Error: Cannot broadcast an empty message."))

    # Run the outbound cellular campaign worker
    sent_count = broadcast_campaign(message_text, location_filter=target_zone)
    
    if sent_count > 0:
        # Log this successful execution to our history database
        log_broadcast(message_text, target_zone)
        msg = f"🎉 Success: Dispatched alert to {sent_count} device(s) in zone [{target_zone}]."
    else:
        msg = "⚠️ Broadcast completed: 0 active subscribers matched the chosen target zone."

    return redirect(url_for("index", success_msg=msg))

@app.route("/webhook/receive-sms", methods=["POST"])
def receive_sms():
    """
    Function (e): Automated Inbound Registration Node.
    Listens for real-time incoming SMS events pushed from the tablet via webhooks,
    extracts the nested payload schema, and registers new subscribers.
    """
    try:
        data = request.get_json()
        
        # Verify the incoming JSON matches the documented SMSGate app payload schema structure
        if data and "payload" in data:
            sms_payload = data["payload"]
            sender_phone = sms_payload.get("sender", "").strip()
            message_body = sms_payload.get("message", "").strip()
            
            print(f"\n[WEBHOOK RECEIVED] Incoming message from {sender_phone}: '{message_body}'")
            
            clean_msg = message_body.upper()
            if clean_msg.startswith("JOIN"):
                # Extract the zone phrase after the spacing modifier (e.g., "JOIN NAKURU" -> "NAKURU")
                parts = clean_msg.split(" ", 1)
                location_zone = parts[1].strip() if len(parts) > 1 else "UNKNOWN"
                
                # Execute database insertion through your data handler service
                saved = save_subscriber(sender_phone, location_zone)
                if saved:
                    print(f"🎯 [SUCCESS] Registered fresh subscriber: {sender_phone} -> {location_zone}")
                    return jsonify({"status": "processed", "registration": "saved", "zone": location_zone}), 200
                else:
                    print(f"⚠️ [REGISTRATION OMITTED] {sender_phone} is already inside database.json.")
                    return jsonify({"status": "processed", "registration": "duplicate"}), 200
                    
            return jsonify({"status": "ignored", "reason": "Message pattern did not match 'JOIN <ZONE>'"}), 200
            
        return jsonify({"status": "error", "message": "Invalid SMSGate schema structure"}), 400

    except Exception as e:
        print(f"💥 [WEBHOOK CRASH] Critical execution fault: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
    
if __name__ == "__main__":
    # Bound to 0.0.0.0 so external nodes on your local network/forwarding can reach port 5001
    app.run(debug=True, host="0.0.0.0", port=5001, use_reloader=False)
