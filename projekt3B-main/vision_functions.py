import cv2
import numpy as np
import depthai as dai
import time
import rtde_receive
import rtde_control

def pixel_to_world(u: float, v: float, H):
    p = np.array([u, v, 1.0], dtype=np.float32)
    world = H @ p
    if abs(world[2]) < 1e-6:
        return None
    world /= world[2]
    return float(world[0]), float(world[1])

def find_red_center(frame_bgr):
    hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
    lower_red1 = np.array([0, 100, 80])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 100, 80])
    upper_red2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)

    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    largest = max(contours, key=cv2.contourArea)
    M = cv2.moments(largest)
    if M["m00"] == 0:
        return None

    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"])
    return cx, cy

def print_target_pose(center_points, robot_ip, z_fixed):
    rtde_r = rtde_receive.RTDEReceiveInterface(robot_ip)

    if center_points is not None:
        cx, cy = center_points
        world = pixel_to_world(cx, cy)
        x_w, y_w = world
        z_w = z_fixed
        tcp_pose = rtde_r.getActualTCPPose()
        target_pose = list(tcp_pose)
        target_pose[0] = x_w
        target_pose[1] = y_w
        target_pose[2] = z_w
        time.sleep(0.5)
        print("Target TCP pose:", target_pose)

    return target_pose

def create_bgr_pipeline():
    with dai.Pipeline() as pipeline:
        cam = pipeline.create(dai.node.Camera).build()
        videoQueue = cam.requestOutput((640, 480)).createOutputQueue()
        pipeline.start()
        while pipeline.isRunning():
            videoIn = videoQueue.get()
            frame = videoIn.getCvFrame()
        return frame
