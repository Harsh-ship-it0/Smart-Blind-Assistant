import cv2
from ultralytics import YOLO
import time
import os
import speech_recognition as sr
import winsound
import threading
import tkinter as tk
from PIL import Image, ImageTk

# Load model
model = YOLO("yolov8n.pt")

recognizer = sr.Recognizer()

running = False

last_warning_time = 0
last_speak_time = 0
last_beep_time = 0

# 🔊 Speak
def speak(text):
    os.system(f'powershell -c "Add-Type –AssemblyName System.Speech; '
              f'(New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\'{text}\');"')

# 🎤 Voice command
def listen_command():
    try:
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=3)
            command = recognizer.recognize_google(audio)
            return command.lower()
    except:
        return ""

# 🎥 Camera loop
def run_camera():
    global running, last_warning_time, last_speak_time, last_beep_time

    cap = cv2.VideoCapture(0)

    while running:
        ret, frame = cap.read()
        if not ret:
            break

        height, width, _ = frame.shape
        results = model(frame, conf=0.5)

        messages = []
        obstacle_objects = []

        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])
                label = model.names[cls]

                x1, y1, x2, y2 = box.xyxy[0]
                box_width = x2 - x1
                center_x = (x1 + x2) / 2

                # Direction
                if center_x < width / 3:
                    position = "left"
                elif center_x < 2 * width / 3:
                    position = "center"
                else:
                    position = "right"

                # Distance
                if box_width > 250:
                    distance = "very close"
                    obstacle_objects.append(label)
                elif box_width > 120:
                    distance = "near"
                else:
                    distance = "far"

                messages.append(f"{label} on {position}, {distance}")

        messages = list(set(messages))
        obstacle_objects = list(set(obstacle_objects))

        current_time = time.time()

        # 🔔 Beep
        if current_time - last_beep_time > 1:
            if obstacle_objects:
                winsound.Beep(2000, 300)
            elif messages:
                winsound.Beep(1000, 200)
            last_beep_time = current_time

        # ⚠️ Warning
        if obstacle_objects and (current_time - last_warning_time > 2):
            speak("Warning " + ", ".join(obstacle_objects) + " very close")
            last_warning_time = current_time

        # 🔊 Normal speech
        elif messages and (current_time - last_speak_time > 5):
            speak(". ".join(messages))
            last_speak_time = current_time

        # Convert image for GUI
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        img = ImageTk.PhotoImage(img)

        video_label.imgtk = img
        video_label.configure(image=img)

    cap.release()

# ▶ Start
def start():
    global running
    if not running:
        running = True
        threading.Thread(target=run_camera).start()

# ⏹ Stop
def stop():
    global running
    running = False

# 🎤 Voice Button
def voice_command():
    cmd = listen_command()
    if "what is in front" in cmd:
        speak("Processing scene")

# GUI Window
root = tk.Tk()
root.title("Smart Blind Assistant")
root.geometry("800x600")

video_label = tk.Label(root)
video_label.pack()

btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)

start_btn = tk.Button(btn_frame, text="Start", command=start, width=15)
start_btn.grid(row=0, column=0, padx=10)

stop_btn = tk.Button(btn_frame, text="Stop", command=stop, width=15)
stop_btn.grid(row=0, column=1, padx=10)

voice_btn = tk.Button(btn_frame, text="Voice Command", command=voice_command, width=15)
voice_btn.grid(row=0, column=2, padx=10)

root.mainloop()
