import time
from vision_functions import VisionSystem
from move_functions import RobotController
from StateMachine import StateMachine, State

# idleState fungerer som en menu, hvor brugeren af programmet kan starte og stoppe programflowet.
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
# Generelt massiv mangel på errorhandling i dette program desværre.
# Fokus har været på at åbne et funktionelt program, men vi har desværre brugt tiden for dårligt til at kunne inkludere gennemgående errorhandling.

class analyzeState(State):
    def Run(self):
        vs.best_candidate = None
        vs.target_pose = []
        vs.init_camera()
        vs.detect_objects(vs.get_frame(), vs.get_all_products(), vs.getHomography())
        vs.select_best_object_v2()
        vs.get_target_pose(rc.getCurrentPose())
        if not vs.target_pose:
            print("No objects found. Returning to idleState.")
            sm.changeState(idleState())
        else:
            print("Objects found. Moving robot.")
            sm.changeState(moveState())

# i moveState bevæger robotcellen sig. Der returneres til analyzeState efter sortering.
class moveState(State):
    def Run(self):
        rc.moveRobot(rc.home_pose, rc.getCurrentPose())
        rc.toleranceCheck(rc.home_pose)
        rc.openGripper()

        rc.moveRobot(vs.target_pose, rc.getCurrentPose())
        rc.toleranceCheck(vs.target_pose)
        rc.closeGripper()

        rc.moveRobot(rc.home_pose, rc.getCurrentPose())
        rc.toleranceCheck(rc.home_pose)

        rc.moveRobot(vs.target_depot, rc.getCurrentPose())
        rc.toleranceCheck(vs.target_depot)
        rc.openGripper()

        rc.moveRobot(rc.home_pose, rc.getCurrentPose())
        rc.toleranceCheck(rc.home_pose)

        sm.changeState(analyzeState())

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
    rc = RobotController("192.168.0.2")
    vs = VisionSystem()
    sm.run()
