#!/usr/bin/env python
#Det her er kun lavet for at vi kan hurtigt lige manualt kan teste vores kalibrerig.
import time

import rtde_control
import rtde_receive

ROBOT_IP = "192.168.0.2"


def main():
    # --- desired XYZ in base frame (meters) ---
    x, y, z =   0.20982763, -0.29314993, 0.02   # <-- change these

    # Connect RTDE interfaces
    rtde_c = rtde_control.RTDEControlInterface(ROBOT_IP)
    rtde_r = rtde_receive.RTDEReceiveInterface(ROBOT_IP)

    print(f"Connected to UR3e at {ROBOT_IP}")

    # Get current TCP pose [x, y, z, Rx, Ry, Rz]
    tcp_pose = rtde_r.getActualTCPPose()
    print("Current TCP pose:", tcp_pose)

    # Build target pose: same orientation, new XYZ
    target_pose = list(tcp_pose)
    target_pose[0] = float(x)
    target_pose[1] = float(y)
    target_pose[2] = float(z)

    print("Target TCP pose:", target_pose)
    print("Moving with moveL...")

    # moveL(target, speed, acceleration)
    rtde_c.moveL(target_pose, 0.25, 0.5)

    # Small wait to ensure motion completes before we exit
    time.sleep(0.5)

    # Stop script on controller side (optional but clean)
    rtde_c.stopScript()
    print("Done.")


if __name__ == "__main__":
    main()