import cv2

from vision_functions import VisionSystem
from move_functions import RobotController
from StateMachine import StateMachine, State
import time

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
        vs.init_camera()
        vs.detect_objects(vs.get_frame(), vs.get_all_products(), vs.getHomography())
        vs.select_best_object(rc.getCurrentPose())
        vs.get_target_pose(rc.getCurrentPose())
        sm.changeState(moveState())

class moveState(State):
    def Run(self):
        rc.moveRobot(rc.home_pose, rc.getCurrentPose())
        rc.openGripper()
        rc.moveRobot(vs.target_pose, rc.getCurrentPose())
        rc.closeGripper()

        rc.moveRobot(rc.home_pose, rc.getCurrentPose())

        rc.moveRobot(vs.target_depot, rc.getCurrentPose())
        rc.openGripper()

        sm.changeState(idleState())

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
    rc = RobotController()
    vs = VisionSystem()
    sm.run()
