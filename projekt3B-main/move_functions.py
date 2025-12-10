import time
import numpy as np
import rtde_control
import rtde_receive
import rtde_io

class RobotController:
    def __init__(self, ROBOT_IP:str):
        self.controlConn = rtde_control.RTDEControlInterface(ROBOT_IP)
        self.recieveConn = rtde_receive.RTDEReceiveInterface(ROBOT_IP)
        self.IOConn = rtde_io.RTDEIOInterface(ROBOT_IP)
        self.home_pose = [-0.06, -0.285, 0.2, 3.14, 0, 0]

    def moveRobot(self, targetPose, currentPose):
        try:
            if not targetPose:
                print("TargetPose is empty.")
                self.controlConn.moveL(self.home_pose, 0.25, 0.5)
            else:
                targetPose[3] = currentPose[3]
                targetPose[4] = currentPose[4]
                targetPose[5] = currentPose[5]
                print(f"Command Move to: {targetPose} Sent to Robot")
                self.controlConn.moveL(targetPose, 0.25, 0.5)  # her i moveL der sætter vi speed og accleartion
        except TypeError:
            print("error in moveRobot function. targetPose is None.")
        except UnboundLocalError:
            print("error in moveRobot function. targetPose referenced before assignment")

    def getCurrentPose(self):
        currentPose = self.recieveConn.getActualTCPPose()
        return currentPose

    def closeGripper(self):
        if not self.recieveConn.getDigitalOutState(16):
            self.IOConn.setToolDigitalOut(0, True)
            time.sleep(1)
        else:
            print("Gripper is already closed!")

    def openGripper(self):
        if self.recieveConn.getDigitalOutState(16):
            self.IOConn.setToolDigitalOut(0, False)
            time.sleep(1)
        else:
            print("Gripper is already open!")

    def toleranceCheck(self, targetPose, currentPose):
        try:
            # tolerance in meters
            pos_tol = 0.005  # 5 mm
            while True:
                # only compare XYZ
                pos_current = np.array(currentPose[:3])
                pos_target = np.array(targetPose[:3])
                # Euclidean distance
                pos_dist = np.linalg.norm(pos_current - pos_target)
                if pos_dist < pos_tol:
                    print("Target position reached within tolerance.")
                    break
                print("Current:", pos_current, "Distance:", pos_dist)
                time.sleep(1)
        except TypeError:
            print("Error in toleranceCheck function. targetPose is None.")

    def hard_coded_poses(self, targetPose):
        x_w, y_w, z_w = targetPose
        tcp_pose = self.recieveConn.getActualTCPPose()
        target_pose = list(tcp_pose)
        target_pose[0] = x_w
        target_pose[1] = y_w
        target_pose[2] = z_w
        print(f"Command Move to: {target_pose} Sent to Robot")
        return target_pose
