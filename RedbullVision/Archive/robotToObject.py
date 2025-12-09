#!/usr/bin/env python3
#Brug det her script til at flytte robotten til en lokation baseret på et rødt objekts position i billedet.
import time

import cv2
import depthai as dai
import numpy as np
import rtde_control
import rtde_receive

ROBOT_IP = "192.168.0.2"

data = np.load("homography.npz")
H = data["H"]

# Fixed Z height in meters
Z_FIXED = 0.05

def pixel_to_world(u: float, v: float):
    p = np.array([u, v, 1.0], dtype=np.float32)
    world = H @ p
    if abs(world[2]) < 1e-6:
        return None
    world /= world[2]
    return float(world[0]), float(world[1])

# samme funktion som kim brugte i sin farve tracking kode men simplificeret lidt i må lige tilføje alt det der gaussien blur og sån noget senere hvis det er nødvendigt
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
    # Tror godt vi kan fjerne RTDEControlInterface og RTDEReceiveInterface og bare skrive rtde(Robot_ip)
    rtde_c = rtde_control.RTDEControlInterface(ROBOT_IP)
    rtde_r = rtde_receive.RTDEReceiveInterface(ROBOT_IP)
    print(f"Connected to UR3e at {ROBOT_IP}")


    # Vi bruger det samme som fra depthai github eksempler så vi undgår xout osv.
    # igen vi må lige snakke sammen om det her senere jeg syntes vi skal holde det som det er her helt simplet.
    # kunne være fedt hvis der var en der undersøgte om vi kunne sætte fokus på kamera via pipeline.
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
                    (35, 0, 70),
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

            cv2.imshow("Vsion obkect tracking", frame)
            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

            if key == ord("g") and red_center is not None:
                cx, cy = red_center
                print(f"Using detected object center pixel: ({cx},{cy})")
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

                #her har vi den her liste gruden til at fordi ligenu får vi ikke vores rotations matrix. så der får tager vi
                # vores current tcp position fra robten så bagefter ændre vi bare de 3 første værdier i arrayet så vores nu værneede
                # rotation på tcp ikke ændre sig vi kan altid bare tilføje vores egen rotation hvis vi vil men eller altid bare 
                # sætte den så den altid peget nedad det må vi lige finde ud af.
                target_pose = list(tcp_pose)
                target_pose[0] = x_w
                target_pose[1] = y_w
                target_pose[2] = z_w

                print("Target TCP pose:", target_pose)
                print("Moving with moveL...")
                rtde_c.moveL(target_pose, 0.25, 0.5) # her i moveL der sætter vi speed og accleartion
                time.sleep(0.5)

    cv2.destroyAllWindows()
    rtde_c.stopScript()
    print("Done.")


if __name__ == "__main__":
    main()