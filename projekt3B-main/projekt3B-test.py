import time
import rtde_receive
import rtde_control
import vision_functions as vf
import move_functions as mf
from StateMachine import StateMachine, State
import numpy as np

# Init af forbindelser til robot RTDE control & recieve interfaces
robot_ip = "192.168.0.2"
conn = rtde_control.RTDEControlInterface(robot_ip)
rec_conn = rtde_receive.RTDEReceiveInterface(robot_ip)


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

# analyseState er hvor behandling af koordinatsystemer, kamerafeed, og billedebehandling foregår.
class analyzeState(State):
    def Run(self):
        data = np.load("homography.npz")
        H = data["H"]
        z_fixed = 0.2
        frame = vf.create_bgr_pipeline()
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
        mf.useGripper(conn,
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
    def Enter(self):
        pass

    def Run(self):
        pass

    def Exit(self):
        pass


if __name__ == "__main__":
    sm = StateMachine(idleState())
    sm.run()
