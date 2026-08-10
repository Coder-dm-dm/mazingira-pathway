import subprocess
from flask import Flask, render_template, request, redirect, url_for, jsonify, Response, stream_with_context

from services.data_handler import get_subscribers, save_manual_subscriber
from services.history_handler import get_broadcast_history, log_broadcast
from services.ai_handler import stream_ai_broadcast, load_settings, save_settings
from services.sms_sender import broadcast_campaign
from services.response_handler import process_inbound_sms, start_adb_daemon

app = Flask(__name__)

# ==========================================
# 1. WEB DASHBOARD ROUTES
# ==========================================

@app.route("/", methods=["GET"])
def index():
    return render_template(
        "index.html",
        registered_numbers=get_subscribers(),
        past_broadcasts=get_broadcast_history(),
        user_prompt=request.args.get("user_prompt", ""),
        generated_text=request.args.get("generated_text", ""),
        success_msg=request.args.get("success_msg", "")
    )


@app.route("/stream-alert", methods=["GET"])
def stream_alert():
    user_prompt = request.args.get("prompt", "").strip()
    use_translator = request.args.get("translate", "true").lower() == "true"
    
    if not user_prompt:
        return jsonify({"error": "No prompt provided"}), 400

    return Response(
        stream_with_context(stream_ai_broadcast(user_prompt, use_translator=use_translator)),
        mimetype="text/event-stream"
    )

@app.route("/toggle-translator", methods=["POST"])
def toggle_translator():
    data = request.get_json() or {}
    enabled = data.get("enabled", True)
    save_settings({"use_translator": enabled})
    return jsonify({"status": "success", "use_translator": enabled})


@app.route("/generate-alert", methods=["POST"])
def generate_alert():
    user_prompt = request.form.get("prompt", "").strip()
    generated_text = generate_ai_broadcast(user_prompt) if user_prompt else ""
    return redirect(url_for("index", user_prompt=user_prompt, generated_text=generated_text))


@app.route("/manual-onboard", methods=["POST"])
def manual_onboard():
    phone = request.form.get("phone", "").strip()
    location = request.form.get("location", "").strip().upper()
    initiative_id = request.form.get("initiative_id", "").strip().upper()
    
    if not phone or not initiative_id:
        return redirect(url_for("index", success_msg="❌ Error: All manual onboarding fields are required."))
        
    saved = save_manual_subscriber(phone, location, initiative_id)
    msg = f"🎯 Registered local resident {phone} to [{location}]." if saved else f"⚠️ Entry Omitted: Subscriber {phone} already exists."
    return redirect(url_for("index", success_msg=msg))


@app.route("/send-broadcast", methods=["POST"])
def send_broadcast():
    message_text = request.form.get("message_text", "").strip()
    target_zone = request.form.get("target_zone", "ALL").strip()
    
    if not message_text:
        return redirect(url_for("index", success_msg="❌ Error: Cannot broadcast an empty message."))

    sent_count = broadcast_campaign(message_text, location_filter=target_zone)
    if sent_count > 0:
        log_broadcast(message_text, target_zone)
        msg = f"🎉 Success: Dispatched broadcast to {sent_count} device(s) in zone [{target_zone}]."
    else:
        msg = "⚠️ Broadcast completed: 0 active subscribers matched the target zone."

    return redirect(url_for("index", success_msg=msg))


@app.route("/clear-phone-logs", methods=["POST"])
def clear_phone_logs():
    try:
        subprocess.run(["adb", "shell", "pm", "clear", "com.android.providers.telephony"], check=True)
        msg = "🧹 Success: Handset message logs wiped clean over ADB link."
    except Exception as e:
        msg = f"⚠️ Housekeeping bypassed: {e}"
    return redirect(url_for("index", success_msg=msg))


# ==========================================
# 2. TWO-WAY AI CHAT-BACK WEBHOOK
# ==========================================

@app.route('/inbound-sms', methods=['POST'])
def handle_inbound_sms():
    data = request.get_json() or request.form or {}
    sender_phone = data.get('sender') or data.get('from') or data.get('phone')
    incoming_text = data.get('message') or data.get('text')

    if not sender_phone or not incoming_text:
        return jsonify({"status": "error", "message": "Missing 'sender' and 'message'"}), 400

    result = process_inbound_sms(sender_phone, incoming_text)
    return jsonify({"status": "success", "result": result}), 200


# ==========================================
# 3. LAUNCHER
# ==========================================

if __name__ == "__main__":
    start_adb_daemon()
    app.run(debug=True, host="0.0.0.0", port=5001, use_reloader=False)