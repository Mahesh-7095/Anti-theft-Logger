import cv2
import smtplib
import ssl
import time
import json
import ctypes
from email.message import EmailMessage
from datetime import datetime
import os
import sys
import traceback

# Load config
with open("config.json", "r") as f:
    config = json.load(f)

EMAIL_ADDRESS = config.get("email")
EMAIL_PASSWORD = os.environ.get("ANTI_THEFT_EMAIL_PASS") or config.get("password")
TO_EMAIL = config.get("to") or config.get("recipient_email") or config.get("recipient")
SMTP_SERVER = config.get("smtp_server", "smtp.gmail.com")
SMTP_PORT = int(config.get("smtp_port", 465))

if not (EMAIL_ADDRESS and EMAIL_PASSWORD and TO_EMAIL):
    print("❌ Missing required config keys. Please ensure 'email', 'password' (or env ANTI_THEFT_EMAIL_PASS), and 'to' are set.")
    sys.exit(1)

# Capture image from webcam
def capture_image():
    cam = None
    try:
        cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # CAP_DSHOW can help on Windows
        if not cam.isOpened():
            print("❌ Webcam not accessible")
            return None
        # Warm up camera a bit
        time.sleep(0.5)
        ret, frame = cam.read()
        if not ret:
            print("❌ Failed to capture image from webcam")
            return None
        if not os.path.exists("captures"):
            os.makedirs("captures", exist_ok=True)
        filename = f"captures/theft_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        cv2.imwrite(filename, frame)
        print(f"📸 Image captured: {filename}")
        return filename
    except Exception as e:
        print(f"❌ Exception during capture: {e}")
        traceback.print_exc()
        return None
    finally:
        if cam is not None and cam.isOpened():
            cam.release()

# Send email with image attachment (tries SSL then TLS as fallback)
def send_email(image_path, max_retries=2):
    msg = EmailMessage()
    msg["Subject"] = "🚨 Theft Alert - Unauthorized Access Detected"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = TO_EMAIL
    msg.set_content("Someone tried to access your laptop! See attached image for evidence.")

    with open(image_path, "rb") as img:
        img_data = img.read()
        msg.add_attachment(img_data, maintype="image", subtype="png", filename=os.path.basename(image_path))

    # Try SMTP_SSL first
    for attempt in range(1, max_retries + 1):
        try:
            context = ssl.create_default_context()
            print(f"🔁 Trying to send email (attempt {attempt}) via SSL {SMTP_SERVER}:{SMTP_PORT} ...")
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context, timeout=15) as server:
                server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                server.send_message(msg)
            print("📧 Email sent successfully!")
            return True
        except smtplib.SMTPAuthenticationError as auth_err:
            print("❌ Authentication failed (SMTPAuthenticationError).")
            print("   • Did you enable 2-Step Verification and create an App Password?")
            print("   • If using Gmail, generate a 16-character app password and put it in config or ANTI_THEFT_EMAIL_PASS.")
            print(f"   • Server message: {auth_err}")
            return False
        except Exception as e:
            print(f"⚠️ SMTP SSL attempt failed: {e}")
            # Try fallback to STARTTLS on port 587 if first attempt was SSL and port was 465
            if SMTP_PORT == 465 and attempt == 1:
                try:
                    print("🔁 Falling back to STARTTLS on smtp.gmail.com:587 ...")
                    context = ssl.create_default_context()
                    with smtplib.SMTP("smtp.gmail.com", 587, timeout=15) as server:
                        server.ehlo()
                        server.starttls(context=context)
                        server.ehlo()
                        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                        server.send_message(msg)
                    print("📧 Email sent successfully via STARTTLS!")
                    return True
                except smtplib.SMTPAuthenticationError:
                    print("❌ Authentication failed during STARTTLS fallback.")
                    return False
                except Exception as e2:
                    print(f"⚠️ STARTTLS fallback failed: {e2}")
            # If last attempt, print stack
            if attempt == max_retries:
                print("❌ All attempts to send email failed.")
                traceback.print_exc()
                return False
            else:
                print("⏳ Retrying...")
                time.sleep(2)

# Wait for session unlock (using kernel32)
def wait_for_unlock():
    print("🕵️ Monitoring session unlock...")
    last_session = None
    while True:
        try:
            kernel32 = ctypes.windll.kernel32
            session_id = kernel32.WTSGetActiveConsoleSessionId()
            if session_id != last_session:
                last_session = session_id
                return
        except Exception as e:
            # If ctypes fails for any reason, break so we don't loop infinitely silently
            print(f"⚠️ Error checking session id: {e}")
            return
        time.sleep(1)

# Main loop
def main():
    wait_for_unlock()
    image_path = capture_image()
    if image_path:
        send_email(image_path)

if __name__ == "__main__":
    main()
