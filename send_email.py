import smtplib
import ssl
import json
from email.message import EmailMessage
import os

# Load config (email credentials)
with open("config.json", "r") as f:
    config = json.load(f)

EMAIL_ADDRESS = config["email"]
EMAIL_PASSWORD = config["app_password"]
RECIPIENT_EMAIL = config["recipient"]

def send_email(image_path):
    msg = EmailMessage()
    msg["Subject"] = "⚠️ Theft Attempt Detected!"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = RECIPIENT_EMAIL
    msg.set_content("Someone tried to access your laptop. Image attached.")

    with open(image_path, "rb") as f:
        img_data = f.read()
        msg.add_attachment(img_data, maintype="image", subtype="png", filename=os.path.basename(image_path))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

    print("📧 Email sent successfully!")
