# fake_login.py
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw
import os
import json
from capture import capture_image
from send_email import send_email

# Load config
with open("config.json") as f:
    config = json.load(f)

CORRECT_PASSWORD = config["app_password"]
RECIPIENT_EMAIL = config["recipient"]
SENDER_EMAIL = config["email"]
APP_PASSWORD = config["app_password"]

# Capture + send if password is wrong
def handle_login():
    entered = password_var.get()
    if entered == CORRECT_PASSWORD:
        messagebox.showinfo("Access Granted", "Welcome back!")
        root.destroy()
    else:
        image_path = capture_image()
        send_email(
            sender=SENDER_EMAIL,
            password=APP_PASSWORD,
            to=RECIPIENT_EMAIL,
            subject="🚨 Unauthorized Access Attempt",
            body="Someone tried to access your system with the wrong password.",
            attachment=image_path
        )
        messagebox.showerror("Access Denied", "Wrong password. Incident reported.")

# Toggle password visibility
def toggle_password():
    if password_entry.cget('show') == "*":
        password_entry.config(show="")
        toggle_btn.config(text="👁")
    else:
        password_entry.config(show="*")
        toggle_btn.config(text="👁‍‍🗨")

root = tk.Tk()
root.title("Login")
root.attributes("-fullscreen", True)
root.configure(bg="#111111")

frame = tk.Frame(root, bg="#111111")
frame.pack(expand=True)


# User image
img_path = "user.png"  # Make sure this exists
original = Image.open(img_path).resize((150, 150))
mask = Image.new("L", original.size, 0)
draw = ImageDraw.Draw(mask)
draw.ellipse((0, 0, 150, 150), fill=255)
result = Image.new("RGBA", original.size)
result.paste(original, (0, 0), mask)
user_img = ImageTk.PhotoImage(result)

user_label = tk.Label(frame, image=user_img, bg="#111111")
user_label.pack(pady=(0, 20))

# Password field with toggle
password_var = tk.StringVar()
password_frame = tk.Frame(frame, bg="#111111")
password_frame.pack(pady=10)

password_entry = tk.Entry(password_frame, textvariable=password_var, show="*", font=("Segoe UI", 16), width=25, relief="flat", highlightthickness=2, highlightcolor="#00BFFF")
password_entry.pack(side=tk.LEFT, ipady=8)

toggle_btn = tk.Button(password_frame, text="👁‍‍🗨", command=toggle_password, relief="flat", bg="#111111", fg="white")
toggle_btn.pack(side=tk.LEFT, padx=10)

# Sign in button
sign_btn = tk.Button(frame, text="Sign In", command=handle_login, font=("Segoe UI", 16), bg="#00BFFF", fg="white", relief="flat", padx=20, pady=10)
sign_btn.pack(pady=20)
sign_btn.config(borderwidth=0, highlightthickness=0)
sign_btn.configure(cursor="hand2")

# Allow Enter key to trigger login
root.bind("<Return>", lambda e: handle_login())

root.mainloop()


# capture.py
import cv2
import os
from datetime import datetime

def capture_image():
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    if not os.path.exists("captures"):
        os.makedirs("captures")
    filename = f"captures/theft_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    if ret:
        cv2.imwrite(filename, frame)
    cam.release()
    return filename


# send_email.py
import smtplib
import ssl
from email.message import EmailMessage

def send_email(sender, password, to, subject, body, attachment):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to
    msg.set_content(body)

    with open(attachment, 'rb') as f:
        file_data = f.read()
        file_name = os.path.basename(attachment)

    msg.add_attachment(file_data, maintype='image', subtype='png', filename=file_name)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(sender, password)
        smtp.send_message(msg)


# config.json (example)
{
  "email": "youremail@gmail.com",
  "app_password": "your_app_password",
  "recipient": "youremail@gmail.com",
  "password": "1234"
}
