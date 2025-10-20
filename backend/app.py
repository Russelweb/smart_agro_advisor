

from flask import Flask, render_template, send_from_directory, request
from flask_cors import CORS
import os
import requests
import threading
import time
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from dotenv import load_dotenv

load_dotenv()

# -----------------------------
# APP CONFIG
# -----------------------------
app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

# Import blueprints
from backend.routes.diagnosis import diagnosis_bp
from backend.routes.weather import weather_bp
from backend.routes.advisory import advisory_bp

# Register blueprints
app.register_blueprint(diagnosis_bp)
app.register_blueprint(weather_bp)
app.register_blueprint(advisory_bp)

# -----------------------------
# TWILIO CONFIG
# -----------------------------
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID2")

TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN2")

TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
# same sandbox number used by both sandboxes normally

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


# -----------------------------
# HELPER — Split & Send Long Messages Safely (robust)
# -----------------------------
def send_long_message(sender, message):
    """
    Safely send a WhatsApp message by splitting into parts and handling Twilio errors.
    - Respects Twilio's ~1600 char per-message limit.
    - Limits parts to MAX_PARTS to avoid flooding.
    - Retries with smaller chunk sizes if Twilio complains about length.
    - Sleeps between parts to reduce chance of 429 rate limits.
    """
    # Initial parameters
    INITIAL_MAX_LEN = 1600   # Twilio's documented limit (~1600 chars)
    MIN_CHUNK = 400          # Don't go below this when retrying
    MAX_PARTS = 5            # Prevent sending excessive parts
    SLEEP_BETWEEN_PARTS = 0.8  # seconds; prevents hitting rate-limits

    def _split_into_parts(text, chunk_size):
        return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

    # Try progressive strategy: start with INITIAL_MAX_LEN, if Twilio complains,
    # retry with smaller chunk sizes down to MIN_CHUNK.
    chunk_size = INITIAL_MAX_LEN

    while chunk_size >= MIN_CHUNK:
        parts = _split_into_parts(message, chunk_size)

        # If too many parts, truncate message to MAX_PARTS * chunk_size
        if len(parts) > MAX_PARTS:
            truncated = message[:chunk_size * MAX_PARTS - 3] + "..."
            parts = _split_into_parts(truncated, chunk_size)

        # Prepare labeled parts if multipart
        labeled_parts = []
        for idx, part in enumerate(parts):
            if len(parts) > 1:
                labeled = f"(Part {idx + 1}/{len(parts)})\n{part}"
            else:
                labeled = part
            labeled_parts.append(labeled)

        # Try sending the labeled parts sequentially
        all_sent = True
        for idx, part in enumerate(labeled_parts):
            try:
                client.messages.create(
                    from_=TWILIO_WHATSAPP_NUMBER,
                    to=sender,
                    body=part
                )
                print(f"[Twilio] Sent part {idx + 1}/{len(labeled_parts)} ({len(part)} chars)")
                # avoid bursting
                time.sleep(SLEEP_BETWEEN_PARTS)

            except TwilioRestException as tre:
                # If Twilio complains about concatenated message body >1600,
                # reduce chunk size and retry the whole message with smaller chunks.
                msg = str(tre)
                print(f"[Twilio][Error] TwilioRestException while sending part {idx + 1}: {msg}")

                if "concatenated message body exceeds the 1600" in msg or "exceeds the 1600" in msg:
                    print(f"[Twilio] Detected 1600-limit error. Reducing chunk size from {chunk_size} and retrying.")
                    all_sent = False
                    break  # break out of sending loop and retry with smaller chunk_size

                # If it's a 429 or rate-limit-ish, wait and retry current part a few times
                if tre.status == 429:
                    retry_wait = 2.0
                    retries = 3
                    sent = False
                    for attempt in range(retries):
                        print(f"[Twilio] 429 received — retrying in {retry_wait}s (attempt {attempt+1}/{retries})")
                        time.sleep(retry_wait)
                        try:
                            client.messages.create(from_=TWILIO_WHATSAPP_NUMBER, to=sender, body=part)
                            print("[Twilio] Retry successful.")
                            sent = True
                            break
                        except TwilioRestException as tre2:
                            print(f"[Twilio] Retry failed: {tre2}")
                            retry_wait *= 2
                    if not sent:
                        print("[Twilio] Could not send part after retries. Aborting this send_long_message call.")
                        return False
                else:
                    # For other Twilio errors, log and try to send an error notice (short)
                    print(f"[Twilio] Unexpected Twilio error: {tre}. Aborting send_long_message.")
                    return False

            except Exception as e:
                # network or other errors
                print(f"[Twilio][Exception] Network/other error while sending part: {e}")
                # don't raise, return failure so caller can handle or log
                return False

        if all_sent:
            # all parts were successfully sent
            return True
        else:
            # we need to retry with a smaller chunk size
            # reduce chunk size (e.g., decrease by 25%)
            new_chunk = int(chunk_size * 0.75)
            if new_chunk >= MIN_CHUNK and new_chunk < chunk_size:
                chunk_size = new_chunk
                print(f"[send_long_message] Retrying with smaller chunk size: {chunk_size}")
                continue
            else:
                # cannot reduce further
                print("[send_long_message] Cannot reduce chunk size further. Aborting.")
                return False

    # If we exit loop without sending anything
    print("[send_long_message] Reached minimum chunk size and still couldn't send.")
    return False


# -----------------------------
# BACKGROUND PROCESS FUNCTION
# -----------------------------
def process_in_background(sender, message_body, image_url):
    try:
        print(f"[Thread] Processing message from {sender}")

        # --- Immediate feedback ---
        send_long_message(sender, "🔄 Analyzing your crop image... please wait a few seconds.")

        if not image_url:
            send_long_message(sender, "🌱 Please send a *crop leaf image* along with your city name (e.g., 'Bamenda').")
            return

        city = message_body or "Unknown"

        # --- Download image securely ---
        try:
            img_response = requests.get(image_url, auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN), timeout=30)
        except Exception as e:
            print(f"[process_in_background] Failed to download image: {e}")
            send_long_message(sender, "⚠️ Couldn't download the image. Please resend a clear photo.")
            return

        if img_response.status_code != 200:
            print(f"[process_in_background] Image download status: {img_response.status_code}")
            send_long_message(sender, "⚠️ Couldn't download the image. Please resend a clear photo.")
            return

        image_path = f"temp_{sender.split(':')[-1]}.jpg"
        with open(image_path, "wb") as f:
            f.write(img_response.content)

        # --- Validate image ---
        if not os.path.exists(image_path) or os.path.getsize(image_path) < 1024:
            send_long_message(sender, "⚠️ The image seems empty or unreadable. Please resend a clear photo.")
            try:
                if os.path.exists(image_path):
                    os.remove(image_path)
            except Exception:
                pass
            return

        # --- Send to local backend (/api/advice) ---
        try:
            with open(image_path, "rb") as img_file:
                files = {"image": img_file}
                data = {"city": city}
                api_res = requests.post("http://127.0.0.1:5000/api/advice/", files=files, data=data, timeout=200)
        except Exception as e:
            print(f"[process_in_background] Error calling /api/advice: {e}")
            send_long_message(sender, "⚠️ Sorry, the Agro Advisor failed to process your request.")
            try:
                os.remove(image_path)
            except Exception:
                pass
            return

        try:
            os.remove(image_path)
        except Exception:
            pass

        if api_res.status_code != 200:
            print(f"[process_in_background] /api/advice returned status {api_res.status_code}")
            send_long_message(sender, "⚠️ Sorry, the Agro Advisor failed to process your request.")
            return

        result = api_res.json()
        print("✅ Advisor response received.")

        crop = result.get("crop", "Unknown crop")
        disease = result.get("disease", {}).get("predicted_label", "Unknown disease")
        advice_list = result.get("advice", ["No advice available."])
        advice_text = advice_list[0] if advice_list else "No advice available."

        # --- Construct reply message ---
        reply_msg = (
            f"🌾 *Smart Agro Advisor*\n\n"
            f"📍 City: {city}\n"
            f"🌱 Crop: {crop}\n"
            f"🦠 Disease: {disease}\n\n"
            f"💡 *Advice:*\n{advice_text}"
        )

        # --- Send message safely (split if needed) ---
        ok = send_long_message(sender, reply_msg)
        if not ok:
            # final fallback: send a short summary so user still receives something
            fallback = (
                f"🌾 Smart Agro Advisor\n\n"
                f"📍 {city}\n"
                f"🌱 {crop}\n"
                f"🦠 {disease}\n\n"
                "💡 Advice: (reply with 'more' to get details)"
            )
            send_long_message(sender, fallback)
            print(f"[Thread] Sent fallback summary to {sender} due to send error.")
        else:
            print(f"[Thread] Reply sent to {sender} successfully.")

    except Exception as e:
        error_msg = f"⚠️ An unexpected error occurred while processing your image.\n\nError details:\n{str(e)}"
        print(f"❌ Background error for {sender}: {e}")
        # use safe sender for error messages too
        send_long_message(sender, error_msg)


# -----------------------------
# WHATSAPP ROUTE (INSTANT RESPONSE)
# -----------------------------
@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    sender = request.form.get("From")
    message_body = request.form.get("Body", "").strip()
    image_url = request.form.get("MediaUrl0")

    print(f"📩 Incoming message from {sender}")
    print(f"💬 Message: {message_body}")
    print(f"🖼 Media URL: {image_url}")

    # --- Launch background thread ---
    threading.Thread(target=process_in_background, args=(sender, message_body, image_url)).start()

    # --- Respond immediately to Twilio ---
    resp = MessagingResponse()
    resp.message("✅ Thanks! Your request is being processed. You’ll get results shortly.")
    return str(resp)


# -----------------------------
# FRONTEND ROUTES
# -----------------------------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory(os.path.join(app.root_path, "static"), filename)


# -----------------------------
# MAIN ENTRY
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)


# -----------------------------
# FRONTEND ROUTES
# -----------------------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory(os.path.join(app.root_path, "static"), filename)

# -----------------------------
# MAIN ENTRY
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
