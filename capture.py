import cv2
import os
from datetime import datetime

def capture_image():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Could not open webcam")

    ret, frame = cap.read()
    cap.release()

    if not ret:
        raise RuntimeError("Failed to capture image")

    if not os.path.exists("captures"):
        os.makedirs("captures")

    filename = f"captures/theft_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    cv2.imwrite(filename, frame)
    print(f"📸 Image captured: {filename}")
    return filename
