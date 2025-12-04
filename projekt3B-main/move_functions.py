import time
import numpy as np

def moveRobot(conn, targetPose):
    try:
        conn.moveL(targetPose, 0.25, 0.5)  # her i moveL der sætter vi speed og accleartion
        print(f"Command Move to: {targetPose} Sent to Robot")
    except TypeError:
        print("error in moveRobot function. targetPose is None.")
    except UnboundLocalError:
        print("error in moveRobot function. targetPose referenced before assignment")

def getCurrentPose(rec_conn):
    currentPose = rec_conn.getActualTCPPose()
    return currentPose

def closeGripper(connIO, rec_conn):
    if not rec_conn.getDigitalOutState(16):
        connIO.setToolDigitalOut(0, True)
        time.sleep(1)
    else:
        print("Gripper is already closed!")

def openGripper(connIO, rec_conn):
    if rec_conn.getDigitalOutState(16):
        connIO.setToolDigitalOut(0, False)
        time.sleep(1)
    else:
        print("Gripper is already open!")
def toleranceCheck(rec_conn, targetPose):
    try:
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
    except TypeError:
        print("Error in toleranceCheck function. targetPose is None.")

def hard_coded_poses(rec_conn, targetPose):
    x_w, y_w, z_w = targetPose
    tcp_pose = rec_conn.getActualTCPPose()
    target_pose = list(tcp_pose)
    target_pose[0] = x_w
    target_pose[1] = y_w
    target_pose[2] = z_w
    print(f"Command Move to: {target_pose} Sent to Robot")
    return target_pose
