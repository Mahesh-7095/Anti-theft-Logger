import cv2
import smtplib
import ssl
import time
import json
import ctypes
from email.message import EmailMessage
from datetime import datetime
import os

# Load config
with open("config.json", "r") as f:
    config = json.load(f)

EMAIL_ADDRESS = config["email"]
EMAIL_PASSWORD = config["password"]
TO_EMAIL = config["to"]

# Capture image from webcam
def capture_image():
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("❌ Webcam not accessible")
        return None
    ret, frame = cam.read()
    cam.release()
    if ret:
        if not os.path.exists("captures"):
            os.makedirs("captures")
        filename = f"captures/theft_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        cv2.imwrite(filename, frame)
        print(f"📸 Image captured: {filename}")
        return filename
    print("❌ Failed to capture image")
    return None

# Send email with image attachment
def send_email(image_path):
    msg = EmailMessage()
    msg["Subject"] = "🚨 Theft Alert - Unauthorized Access Detected"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = TO_EMAIL
    msg.set_content("Someone tried to access your laptop!")

    with open(image_path, "rb") as img:
        img_data = img.read()
        msg.add_attachment(img_data, maintype="image", subtype="png", filename=os.path.basename(image_path))

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        print("📧 Email sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

# Wait for session unlock (using kernel32)
def wait_for_unlock():
    print("🕵️ Monitoring session unlock...")
    last_session = None
    while True:
        kernel32 = ctypes.windll.kernel32
        session_id = kernel32.WTSGetActiveConsoleSessionId()
        if session_id != last_session:
            last_session = session_id
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
