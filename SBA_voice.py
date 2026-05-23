import cv2
from ultralytics import YOLO
import pyttsx3

# voice engine start
engine = pyttsx3.init()

# YOLO model load
model = YOLO("yolov8n.pt")

# camera start
camera = cv2.VideoCapture(0)

spoken_objects = set()

while True:
    ret, frame = camera.read()

    if not ret:
        break

    results = model(frame)

    detected_objects = []

    for r in results:
        boxes = r.boxes
        for box in boxes:
            cls = int(box.cls[0])
            label = model.names[cls]
            detected_objects.append(label)

    # voice output (duplicate avoid)
    for obj in detected_objects:

        engine.say(obj + " detected")
        engine.runAndWait()

    annotated_frame = results[0].plot()

    cv2.imshow("Smart Blind Assistant", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()
