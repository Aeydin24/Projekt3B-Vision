
import time
import numpy as np

def moveRobot(conn, targetPose):
    print("Target TCP pose:", targetPose)
    conn.moveL(targetPose, 0.25, 0.5)  # her i moveL der sætter vi speed og accleartion
    time.sleep(0.5)
    print(f"Command Move to: {targetPose} Sent to Robot")


def getCurrentPose(rec_conn):
    currentPose = rec_conn.getActualTCPPose()
    return currentPose

def closeGripper(connIO):
    connIO.setToolDigitalOut(0, False)

def openGripper(connIO):
    connIO.setToolDigitalOut(0, True)

def toleranceCheck(rec_conn, targetPose):
    # tolerance in meters
    pos_tol = 0.005  # 5 mm

    while True:
        currentPose = getCurrentPose(rec_conn)

        # only compare XYZ
        pos_current = np.array(currentPose[:3])
        pos_target = np.array(targetPose[:3])

        # Euclidean distance
        pos_dist = np.linalg.norm(pos_current - pos_target)

        if pos_dist < pos_tol:
            print("Target position reached within tolerance.")
            break

        print("Moving to target position...")
        print("Current:", pos_current, "Distance:", pos_dist)
        time.sleep(1)


