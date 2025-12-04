import os
import csv
from datetime import datetime

import depthai as dai
import cv2
import numpy as np

# ---------- Konfiguration ----------
LOG_DIR = "vision_logs"
LOG_FILE = os.path.join(LOG_DIR, "vision_log.csv")

VIEW_WIN = "OAK-D PoE - RGB / Color / Mask / Edges"
CTRL_WIN = "Controls"

last_frame = None
last_combined = None

def nothing(x):
    pass

def clamp(val, low, high):
    return max(low, min(high, val))

# ---------- Mouse callback ----------
def on_mouse(event, x, y, flags, param):
    global last_frame
    if event != cv2.EVENT_LBUTTONDOWN or last_frame is None:
        return

    h, w, _ = last_frame.shape
    if x >= w or y >= h:
        return

    bgr = last_frame[y, x].reshape(1, 1, 3)
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)[0, 0]

    H, S, V = int(hsv[0]), int(hsv[1]), int(hsv[2])
    print(f"Klik: HSV=({H},{S},{V})")

    cv2.setTrackbarPos("H min", CTRL_WIN, clamp(H - 10, 0, 179))
    cv2.setTrackbarPos("H max", CTRL_WIN, clamp(H + 10, 0, 179))
    cv2.setTrackbarPos("S min", CTRL_WIN, clamp(S - 60, 0, 255))
    cv2.setTrackbarPos("S max", CTRL_WIN, clamp(S + 60, 0, 255))
    cv2.setTrackbarPos("V min", CTRL_WIN, clamp(V - 60, 0, 255))
    cv2.setTrackbarPos("V max", CTRL_WIN, clamp(V + 60, 0, 255))

# ---------- Logging ----------
def ensure_log():
    os.makedirs(LOG_DIR, exist_ok=True)
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow([
                "ID",
                "Timestamp",
                "H_min", "H_max",
                "S_min", "S_max",
                "V_min", "V_max",
                "Canny_min", "Canny_max",
                "MinR", "MaxR",
                "ImagePath",
                "Comment"
            ])

def next_id():
    if not os.path.exists(LOG_FILE):
        return "VISION_001"
    count = sum(1 for _ in open(LOG_FILE, "r", encoding="utf-8")) - 1
    return f"VISION_{count + 1:03d}"

def log_current(hmin, hmax, smin, smax, vmin, vmax, cmin, cmax, minR, maxR, image):
    ensure_log()
    ID = next_id()

    img_file = f"{ID}.png"
    img_path = os.path.join(LOG_DIR, img_file)
    cv2.imwrite(img_path, image)

    comment = input("Kommentar: ")

    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow([
            ID,
            datetime.now().isoformat(" ", "seconds"),
            hmin, hmax,
            smin, smax,
            vmin, vmax,
            cmin, cmax,
            minR, maxR,
            img_file,
            comment
        ])

    print(f"[LOG] {ID} gemt\n")

# ---------- UI ----------
cv2.namedWindow(CTRL_WIN)
cv2.resizeWindow(CTRL_WIN, 400, 500)
cv2.namedWindow(VIEW_WIN)
cv2.setMouseCallback(VIEW_WIN, on_mouse)

# HSV sliders
cv2.createTrackbar("H min", CTRL_WIN, 0, 179, nothing)
cv2.createTrackbar("H max", CTRL_WIN, 179, 179, nothing)
cv2.createTrackbar("S min", CTRL_WIN, 0, 255, nothing)
cv2.createTrackbar("S max", CTRL_WIN, 255, 255, nothing)
cv2.createTrackbar("V min", CTRL_WIN, 0, 255, nothing)
cv2.createTrackbar("V max", CTRL_WIN, 255, 255, nothing)

# Circle size sliders
cv2.createTrackbar("Min R", CTRL_WIN, 10, 200, nothing)
cv2.createTrackbar("Max R", CTRL_WIN, 100, 300, nothing)

# Canny sliders
cv2.createTrackbar("Canny min", CTRL_WIN, 50, 255, nothing)
cv2.createTrackbar("Canny max", CTRL_WIN, 150, 255, nothing)

# ---------- FASTLÅST Pipeline (IKKE ÆNDRET) ----------
pipeline = dai.Pipeline()

cam = pipeline.create(dai.node.ColorCamera)
cam.setVideoSize(640, 480)
cam.setInterleaved(False)
cam.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)

video_queue = cam.video.createOutputQueue()

print("Starter OAK-D PoE pipeline...")
pipeline.start()
ensure_log()

print("Taster:")
print("  q = quit")
print("  l = log måling")
print("Klik i billedet for at hente HSV")

# ---------- Main loop ----------
while pipeline.isRunning():

    video = video_queue.get()
    frame = video.getCvFrame()
    last_frame = frame.copy()
    circle_layer = frame.copy()

    # Sliders
    hmin = cv2.getTrackbarPos("H min", CTRL_WIN)
    hmax = cv2.getTrackbarPos("H max", CTRL_WIN)
    smin = cv2.getTrackbarPos("S min", CTRL_WIN)
    smax = cv2.getTrackbarPos("S max", CTRL_WIN)
    vmin = cv2.getTrackbarPos("V min", CTRL_WIN)
    vmax = cv2.getTrackbarPos("V max", CTRL_WIN)

    minR = cv2.getTrackbarPos("Min R", CTRL_WIN)
    maxR = cv2.getTrackbarPos("Max R", CTRL_WIN)

    cmin = cv2.getTrackbarPos("Canny min", CTRL_WIN)
    cmax = cv2.getTrackbarPos("Canny max", CTRL_WIN)

    if cmax <= cmin:
        cmax = cmin + 1

    # HSV maske
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower = np.array([hmin, smin, vmin], dtype=np.uint8)
    upper = np.array([hmax, smax, vmax], dtype=np.uint8)
    mask = cv2.inRange(hsv, lower, upper)
    color_only = cv2.bitwise_and(frame, frame, mask=mask)

    # Grå + canny
    gray = cv2.cvtColor(color_only, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 1.0)
    edges = cv2.Canny(blur, cmin, cmax)

    # Hough cirkler
    circles = cv2.HoughCircles(
        gray,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=10, # minimum distance mellem cirkler
        param1=cmax, # Canny øvre threshold
        param2=10,   # sensitivitet
        minRadius=minR, 
        maxRadius=maxR
    )

    circle_layer = frame.copy()
    if circles is not None:
        circles = np.uint16(np.around(circles[0]))
        for x, y, r in circles:
            cv2.circle(circle_layer, (x, y), r, (0,255,0), 2)
            cv2.circle(circle_layer, (x, y), 2, (0,0,255), 3)

    # Combine view
    mask_bgr = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    edges_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

    top = np.hstack((frame, circle_layer))
    bottom = np.hstack((mask_bgr, edges_bgr))
    combined = np.vstack((top, bottom))

    last_combined = combined.copy()
    cv2.imshow(VIEW_WIN, combined)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
    elif key == ord("l"):
        log_current(hmin, hmax, smin, smax, vmin, vmax, cmin, cmax, minR, maxR, combined)

cv2.destroyAllWindows()
