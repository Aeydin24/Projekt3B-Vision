import time
import rtde_receive
import rtde_control
import rtde_io
import vision_functions as vf
import move_functions as mf
from StateMachine import StateMachine, State
import numpy as np

# Init af forbindelser til robot RTDE control & recieve interfaces
robot_ip = "192.168.0.2"
conn = rtde_control.RTDEControlInterface(robot_ip)
connIO = rtde_io.RTDEIOInterface(robot_ip)
rec_conn = rtde_receive.RTDEReceiveInterface(robot_ip)
frame = vf.create_bgr_pipeline()

# idleState fungerer som en menu, hvor brugeren af programmet kan starte og stoppe programflowet.
# OBS: SKAL UDBYGGES - MÅSKE LILLE START/STOP GUI?
class idleState(State):

    def Run(self):
        userIn = input("Enter a command (start/quit): ")
        if userIn == "quit":
            exit(0)
        elif userIn == "start":
            sm.changeState(analyzeState())
        else:
            print("Invalid command")
            sm.changeState(idleState())

# analyseState er hvor behandling af koordinatsystemer og billedbehandling via contours foregår.
class analyzeState(State):
    def Run(self):
        try:
            data = np.load("homography.npz")
            H = data["H"]
        except FileNotFoundError:
            print("File has not been found. Make sure you have a file in the same directory called 'homography.npz'")
            sm.changeState(errorState())
        z_fixed = 0.2
        time.sleep(2)
        center_point = vf.find_red_center(frame)
        sm.targetPose = vf.print_target_pose(center_point,
                                             z_fixed,
                                             H,
                                             rec_conn)
        sm.changeState(moveState())

class moveState(State):
    def Run(self):
        mf.moveRobot(conn,
                     sm.targetPose)
        mf.toleranceCheck(rec_conn,
                          sm.targetPose)
        time.sleep(1)
        targetPose = sm.home
        mf.moveRobot(conn,
                     targetPose)
        mf.toleranceCheck(rec_conn,
                          targetPose)
        print("Successfully reached home")
        time.sleep(1)
        targetPose = sm.redDepot
        mf.moveRobot(conn,
                     targetPose)
        mf.toleranceCheck(rec_conn,
                          targetPose)
        mf.useGripper(connIO,
                      80,
                      40)
        # Grib om emne her
        # mf.useGripper(robot_ip, 30, 40)
        # Skift targetPose til ny pose
        # sm.targetPose = []
        # Kør mod sorteringsplads
        # mf.moveRobot(conn, sm.targetPose)
        # Slip emne
        # mf.useGripper(robot_ip, 0, 0)
        # sm.changeState(idleState())

    def Exit(self):
        pass


class errorState(State):

    def Run(self):
        userIn = input("An error has occurred. Type 'quit' to terminate the program or type 'acknowledge' to acknowledge the error and return to idleState.")
        if userIn == "quit":
            exit(0)
        elif userIn == "acknowledge":
            sm.changeState(idleState())
        else:
            print("Invalid command")
            sm.changeState(idleState())

if __name__ == "__main__":
    sm = StateMachine(idleState())
    sm.run()
