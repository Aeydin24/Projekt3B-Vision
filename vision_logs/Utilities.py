# Utilities.py
import cv2
import numpy as np
import depthai as dai


# ---------------------------------------------------------
#  CIRCLE DETECTION 
# ---------------------------------------------------------


def detect_circles(gray):
    blur = cv2.medianBlur(gray, 3)
    circles = cv2.HoughCircles(
        blur,
        cv2.HOUGH_GRADIENT,
        dp=1,           # inverse ratio of resolution
        minDist=100,    # minimum distance between circles
        minRadius= 35,  # minium radius
        maxRadius=45,   # maksimum radius
        param1=1,       # upper threshold for Canny
        param2=70       # sensitivity
    )
    return circles


# ---------------------------------------------------------
#  SQUARE DETECTION 
# ---------------------------------------------------------


def detect_squares(gray):
    blur = cv2.GaussianBlur(gray, (5, 5), 2)
    edges = cv2.Canny(blur, 50, 150, apertureSize=3)
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    squares = []

    for cnt in contours:
        epsilon = 0.05 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)
        if len(approx) == 4:
            area = cv2.contourArea(approx)
            if area > 200:
                squares.append(approx)

    return squares


# ---------------------------------------------------------
#  COLOR DETECTION 
# ---------------------------------------------------------
def detectColors(frame_bgr, x, y, r):
    x1, y1 = max(0, x - r), max(0, y - r)
    x2, y2 = min(x + r, frame_bgr.shape[1]), min(y + r, frame_bgr.shape[0])

    roi = frame_bgr[y1:y2, x1:x2]
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    lower_red1 = np.array([0, 120, 80])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])

    lower_green = np.array([40, 40, 40])
    upper_green = np.array([80, 255, 255])

    lower_yellow = np.array([25, 100, 100])
    upper_yellow = np.array([35, 255, 255])

    mask_red = cv2.inRange(hsv, lower_red1, upper_red1) | cv2.inRange(hsv, lower_red2, upper_red2)
    mask_green = cv2.inRange(hsv, lower_green, upper_green)
    mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)

    counts = {
        "red": cv2.countNonZero(mask_red),
        "green": cv2.countNonZero(mask_green),
        "yellow": cv2.countNonZero(mask_yellow)
    }

    return max(counts, key=counts.get)


# ---------------------------------------------------------
# VIDEO FRAME
# ---------------------------------------------------------

def getVideo(videoQueue):
    packet = videoQueue.tryGet()
    if packet is None:
        return None
    return packet.getCvFrame()


# ---------------------------------------------------------
# VISIONSANALYSE 
# ---------------------------------------------------------
def analyzeFrame(frame):
    """
    Analyserer et frame og returnerer en liste af objekter.
    Bruges af AnalyzeState.
    """
    objects = []

    if frame is None:
        return objects

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 1) Find cirkler
    circles = detect_circles(gray)

    if circles is not None:
        circles = np.uint16(np.around(circles))

        for c in circles[0]:
            x, y, r = int(c[0]), int(c[1]), int(c[2])

            # 2) Find farve i ROI
            color = detectColors(frame, x, y, r)

            # 3) Tilføj objekt til listen
            objects.append({
                "shape": "circle",
                "x": x,
                "y": y,
                "r": r,
                "color": color
            })

    # Returner alt fundet — også hvis tom

    return objects
    # ---- Squares kan tilføjes senere ----



# ---------------------------------------------------------
#  ROBOT KONTROL
# ---------------------------------------------------------

# Pixel → world funktion
def pixel_to_world(u, v, H):
    p = np.array([u, v, 1.0], dtype=np.float32)
    world = H @ p
    if abs(world[2]) < 1e-6:
        return None
    world /= world[2]
    return float(world[0]), float(world[1])


# ---------------------------------------------------------
#  MOVE TO TARGET
# ---------------------------------------------------------

def moveTo(target, system):
    # Pixel → world
    px = target["x"]
    py = target["y"]

    result = pixel_to_world(px, py)
    if result is None:
        return True

    wx, wy = result
    wz = 0.2  # fast, sikker højde

    tcp = system.rtde_r.getActualTCPPose()
    target_pose = list(tcp)

    dx = wx - target_pose[0]
    dy = wy - target_pose[1]
    dz = wz - target_pose[2]

    mx = np.clip(dx, -system.max_xy_step, system.max_xy_step)
    my = np.clip(dy, -system.max_xy_step, system.max_xy_step)
    mz = np.clip(dz, -system.max_xy_step, system.max_xy_step)

    target_pose[0] += mx
    target_pose[1] += my
    target_pose[2] += mz

    system.rtde_c.servoL(
        target_pose,
        0.2,            # speed
        0.2,            # acceleration  
        system.dt,
        0.03,           # lookahead time
        300             # gain
    )

    return abs(dx) < 0.003 and abs(dy) < 0.003


# ---------------------------------------------------------
#  DROP OFF POSITIONS (KASSE)
# ---------------------------------------------------------


DROP_OFF_POINTS = {
    "red":    (0.20, -0.30, 0.25),
    "green":  (0.25, -0.30, 0.25),
    "yellow": (0.30, -0.30, 0.25)
}

# ---------------------------------------------------------
#  GET TO DROP OFF POSITIONS (KASSE)
# ---------------------------------------------------------
def getDropOffPosition(color):
    return DROP_OFF_POINTS.get(color, None)
# ---------------------------------------------------------
#  MOVE TO DROP OFF POSITION
# ---------------------------------------------------------

def moveToColorSpot(dropTarget, system):


    tx, ty, tz = dropTarget

    tcp = system.rtde_r.getActualTCPPose()
    target_pose = list(tcp)

    dx = tx - target_pose[0]
    dy = ty - target_pose[1]
    dz = tz - target_pose[2]

    mx = np.clip(dx, -system.max_xy_step, system.max_xy_step)
    my = np.clip(dy, -system.max_xy_step, system.max_xy_step)
    mz = np.clip(dz, -system.max_xy_step, system.max_xy_step)

    target_pose[0] += mx
    target_pose[1] += my
    target_pose[2] += mz

    system.rtde_c.servoL(
        target_pose,
        0.5,
        0.5,
        system.dt,
        0.03,
        300
    )

    return abs(dx) < 0.003 and abs(dy) < 0.003


# ---------------------------------------------------------
#  CAMERA INITIALIZATION AND FRAME RETRIEVAL
# -------------------------------------------------------


_pipeline = None
_videoQueue = None

def initCamera():
    global _pipeline, _videoQueue

    # ---------- PIPELINE (LÅST – MÅ IKKE ÆNDRES) ----------
    pipeline = dai.Pipeline()

    cam = pipeline.create(dai.node.ColorCamera)
    cam.setVideoSize(640, 480)
    cam.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
    cam.setInterleaved(False)   # ufarlig, påvirker ikke pipelinen

    video_queue = cam.video.createOutputQueue(maxSize=1, blocking=False)

    print("[CAMERA] Starter pipeline...")

    
    pipeline.start()

    _pipeline = pipeline
    _videoQueue = video_queue


def getVideo():
    """
    Returnerer 1 frame fra OAK-D.
    Kald initCamera() først.
    """
    if _videoQueue is None:
        raise RuntimeError("Camera is not initialized (call initCamera() first)")

    packet = _videoQueue.get()
    return packet.getCvFrame()

"""    tx, ty, tz = dropTarget

    tcp = system.rtde_r.getActualTCPPose()
    target_pose = list(tcp)

    dx = tx - target_pose[0]
    dy = ty - target_pose[1]
    dz = tz - target_pose[2]

    mx = np.clip(dx, -system.max_xy_step, system.max_xy_step)
    my = np.clip(dy, -system.max_xy_step, system.max_xy_step)
    mz = np.clip(dz, -system.max_xy_step, system.max_xy_step)

    target_pose[0] += mx
    target_pose[1] += my
    target_pose[2] += mz

    system.rtde_c.servoL(
        target_pose,
        0.5,
        0.5,
        system.dt,
        0.03,
        300
    )

    if abs(dx) < 0.002 and abs(dy) < 0.002:
        print("[UR] Dropped off object.")
        return True

    return False
# ---------------------------------------------------------
#  MOVE TO HOVER POSITION
# ---------------------------------------------------------

def moveToHover(target, system):
    px = target["x"]
    py = target["y"]

    world = pixel_to_world(px, py)
    if world is None:
        return True

    wx, wy = world
    wz = 0.25   # hover height

    return _moveToWorld(wx, wy, wz, system)

# ---------------------------------------------------------
#  MOVE Z (UP/DOWN)
# ---------------------------------------------------------

def moveZ(system, down):
    tcp = system.rtde_r.getActualTCPPose()
    target = list(tcp)

    hover_z = 0.25
    pick_z  = 0.18

    target[2] = pick_z if down else hover_z

    dx = abs(target[2] - tcp[2])
    mz = np.clip(target[2] - tcp[2], -0.005, 0.005)

    target[2] = tcp[2] + mz

    system.rtde_c.servoL(
        target,
        0.5, 0.5, system.dt, 0.03, 300
    )

    return dx < 0.002

# ---------------------------------------------------------
#  SIMULATE GRAB (placeholder)
# ---------------------------------------------------------

def simulateGrab():
    print("[GRIPPER] (simulated) gripping object...")
# ---------------------------------------------------------
#  INTERNAL: MOVE TO WORLD TARGET
# ---------------------------------------------------------

def _moveToWorld(wx, wy, wz, system):
    tcp = system.rtde_r.getActualTCPPose()
    target = list(tcp)

    dx = wx - target[0]
    dy = wy - target[1]
    dz = wz - target[2]

    mx = np.clip(dx, -system.max_xy_step, system.max_xy_step)
    my = np.clip(dy, -system.max_xy_step, system.max_xy_step)
    mz = np.clip(dz, -system.max_xy_step, system.max_xy_step)

    target[0] += mx
    target[1] += my
    target[2] += mz

    system.rtde_c.servoL(target, 0.5, 0.5, system.dt, 0.03, 300)

    return abs(dx) < 0.002 and abs(dy) < 0.002 and abs(dz) < 0.002



# ---------------------------------------------------------
# INTERNAL: Simuleret robotbevægelse mod world-mål
# ---------------------------------------------------------

_simpos = [0.0, 0.0, 0.20]



def _simulateMove(worldTarget):
    global _simpos

    tx, ty, tz = worldTarget
    rx, ry, rz = _simpos

    speed = 0.005  # 5mm

    def step(a, b):
        if abs(a - b) < speed:
            return b
        return a + speed if b > a else a - speed

    rx = step(rx, tx)
    ry = step(ry, ty)
    rz = tz  # fast højde

    _simpos = [rx, ry, rz]

    print(f"[SIM] Moving to world: {(_simpos[0], _simpos[1], _simpos[2])}")

    # Close enough?
    if abs(rx - tx) < 0.002 and abs(ry - ty) < 0.002:
        print("[SIM] World target reached.")
        return True

    return False
"""""

