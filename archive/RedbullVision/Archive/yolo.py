import cv2
import numpy as np
from ultralytics import YOLO
import torch

print("CUDA available:", torch.cuda.is_available())
DEVICE = 0 if torch.cuda.is_available() else 'cpu'
print("Using device:", DEVICE)
print(torch.cuda.get_device_name(0))


model = YOLO("yolo11n.pt")

url = "http://192.168.1.32:8080/video"
cap = cv2.VideoCapture(url)

while True:
    camera, frame = cap.read()
    if not camera:
        print("Failed to grab frame")
        break

    if frame is not None:        

        yoloFrame = model(frame, device=DEVICE, verbose=False, classes=[0], conf=0.8)


        person_detected = False

        for r in yoloFrame:
            if len(r.boxes) > 0:   # YOLO detected something
                person_detected = True
                print("Person detected!")
        
        annotated = yoloFrame[0].plot()
        cv2.imshow("Safety Camera / YOLO view", annotated)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
