#!/usr/bin/env python3

import time

import cv2
import depthai as dai
import numpy as np
import rtde_control
import rtde_receive

ROBOT_IP = "192.168.0.2"

image_points = np.array([
 [269.20438, 231.23853],

 [282.9418,  231.40858],

 [296.31116, 231.70386],

 [309.9476,  232.38803],

 [323.8921,  232.57532],

 [337.60565, 232.75604],

 [351.3533,  233.22455],

 [365.01834, 233.60591],

 [378.67422, 233.7799 ],

 [268.841,   244.78584],

 [282.4767,  245.30753],

 [296.24783, 245.46617],

 [309.68488, 245.74896],

 [323.53073, 246.2915 ],

 [337.2779,  246.68903],

 [350.79984, 247.12007],

 [364.67224, 247.39052],

 [378.59515, 247.61728],

 [268.43887, 258.54147],

 [282.13168, 258.77237],

 [295.53882, 259.06018],

 [309.52545, 259.63516],

 [323.3153,  260.05283],

 [336.7843,  260.45132],

 [350.52014, 260.5951 ],

 [364.50082, 260.87234],

 [378.23056, 261.40582],

], dtype=np.float32)

world_points_3d = np.array([
    [0.2098560205445687, -0.293125853083126, 0.013670630725627242],
    [0.209401954589718, -0.2711256346025363, 0.013327877648154018],
    [0.20906502743724822, -0.24926116182991437, 0.012543638832057252],
    [0.20886240887486554, -0.2271302512621807, 0.012373404279126837],
    [0.20848766396196963, -0.20496313139630995, 0.012252829778616692],
    [0.20817273788347945, -0.1833259801173631, 0.012114139819924513],
    [0.20799476694021798, -0.16106631569378776, 0.011995707524490473],
    [0.207554489730145, -0.13910713469294328, 0.011871996935032408],
    [0.20717687477421276, -0.11687377850645889, 0.011677309991467183],
    [0.2313415527416441, -0.2928574327410153, 0.013715861589905759],
    [0.23138952164952167, -0.27047358878534444, 0.01348850467954757],
    [0.23091004698025958, -0.24878923358197233, 0.01308993966585642],
    [0.2305819127654663, -0.22668289622554644, 0.012725113441341501],
    [0.23011073131476434, -0.20464560686009842, 0.012684423402256478],
    [0.2301156497310216, -0.18285351131535602, 0.012497146266276904],
    [0.22987321764270285, -0.16080497669021565, 0.012233394577078532],
    [0.22921479477099643, -0.13865024288466585, 0.011873158813579088],
    [0.2293125978978605, -0.11655679055724535, 0.01195326730542165],
    [0.25346812705447275, -0.292586145697203, 0.014110253289649821],
    [0.25332253282965933, -0.27032362248368796, 0.013643912310361911],
    [0.2530193077137687, -0.24821718364583117, 0.01357129172604421],
    [0.2525028388694907, -0.226512226207693, 0.012994836393279308],
    [0.25232225737581687, -0.2042546586583563, 0.013091883638745583],
    [0.2521291762231683, -0.18194358434045882, 0.012694146761365294],
    [0.251566597211971, -0.1599515597186626, 0.012447728266800878],
    [0.2515184408421431, -0.13816584516870278, 0.012483650489861761],
    [0.25077065872364485, -0.1162147352399853, 0.0121665226592364]
], dtype=np.float32)

world_points = world_points_3d[:, :2]

# Compute homography once
H, _ = cv2.findHomography(image_points, world_points)

# Fixed Z height in meters
Z_FIXED = 0.05


def pixel_to_world(u: float, v: float):
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


def main():
    # RTDE robot interfaces
    rtde_c = rtde_control.RTDEControlInterface(ROBOT_IP)
    rtde_r = rtde_receive.RTDEReceiveInterface(ROBOT_IP)
    print(f"Connected to UR3e at {ROBOT_IP}")

    # DepthAI v3 example-style pipeline
    with dai.Pipeline() as pipeline:
        cam = pipeline.create(dai.node.Camera).build()
        videoQueue = cam.requestOutput((640, 480)).createOutputQueue()

        pipeline.start()
        print("Camera started. Press 'g' to move to red object, 'q' to quit.")

        red_center = None

        while pipeline.isRunning():
            videoIn = videoQueue.get()
            frame = videoIn.getCvFrame()

            red_center = find_red_center(frame)
            if red_center is not None:
                cx, cy = red_center
                cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)
                cv2.putText(
                    frame,
                    f"{cx},{cy}",
                    (cx + 5, cy - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 100, 200),
                    2,
                )
                cv2.putText(
                    frame,
                    "Press 'g' to move here",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 0, 255),
                    2,
                )
            else:
                cv2.putText(
                    frame,
                    "No red object",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 0, 255),
                    2,
                )

            cv2.imshow("OAK-D red tracking", frame)
            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

            if key == ord("g") and red_center is not None:
                cx, cy = red_center
                print(f"Using red center pixel: ({cx},{cy})")
                world = pixel_to_world(cx, cy)
                if world is None:
                    print("Homography mapping failed.")
                    continue

                x_w, y_w = world
                z_w = Z_FIXED
                print("Mapped world coordinates (x,y,z):", x_w, y_w, z_w)

                # Get current TCP pose and build target pose
                tcp_pose = rtde_r.getActualTCPPose()
                print("Current TCP pose:", tcp_pose)

                target_pose = list(tcp_pose)
                target_pose[0] = x_w
                target_pose[1] = y_w
                target_pose[2] = z_w

                print("Target TCP pose:", target_pose)
                print("Moving with moveL...")
                rtde_c.moveL(target_pose, 0.25, 0.5)
                time.sleep(0.5)

    cv2.destroyAllWindows()
    rtde_c.stopScript()
    print("Done.")


if __name__ == "__main__":
    main()