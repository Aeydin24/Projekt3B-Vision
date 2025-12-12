from stateMachine import stateMachine, state, stateValues
import detectObject
import moveRobot
from camPipelineV4 import camPipeline
import threading
import time
import dashboard_client
ROBOT_IP = "192.168.0.2"

# note til mig selv gør så man kan skriv reboot så vi manualt kan reboot camPipeline tråden
class idleState(state):
    def Enter(self):
        print("WE ARE NOW IN IDLESTATE")
        if not camPipeline.initFlag:
            print("Starting camera pipeline thread")
            threading.Thread(name='display frame', target=camPipeline.display_frame).start()  
        self.Run()

    def Run(self):

        userIn = input("Enter a command (start/vizmode):")
        if userIn == "start":
            sm.changeState(analyzeState()) 
        elif userIn == "vizmode":
            camPipeline.vizualize = not camPipeline.vizualize
            print(f"Vizualize mode set to: {camPipeline.vizualize}")
            #note skal måske change to idle state again
        else:
            print("Invalid command")        
    # skriv at du er i idle state hvert 10 sekund
    # if start command received, change to analyseState

class moveState(state):
    def Enter(self):
        print("WE ARE NOW IN MOVESTATE")
        self.Run()

    def Run(self):
        # Hent target_pose og alt de ander fra statemachine (sat i analyzeState)
        target_pose = stateValues.target_pose
        target_depot = stateValues.target_depot
        home_pose = stateValues.home_pose
        fixed_height = True 
        print("moveState: åbner gripper")
        moveRobot.openGripper()
        moveRobot.move_to_target(home_pose)
        moveRobot.move_to_target(target_pose, fixed_height)
        print("moveState: bevæger mod target:")
        moveRobot.move_to_target(target_pose)
        print("moveState: lukker gripper")
        moveRobot.closeGripper()
        print("moveState: bevæger mod home:")
        moveRobot.move_to_target(home_pose)
        print("moveState: bevæger mod depot:", target_depot)
        moveRobot.move_to_target(target_depot)
        print("moveState: åbner gripper")
        moveRobot.openGripper()
        print("moveState: bevæger mod home:")
        moveRobot.move_to_target(home_pose)
        time.sleep(1)
        sm.changeState(analyzeState())

    def Exit(self):
        pass


class errorState(state):
    def Enter(self):
        print("WE ARE NOW IN ERRORSTATE")
        self.Run()   
    
    def Run(self):

        print("Robot in protective stop. Please resolve the issue and type 'reset' to continue.")
        while True:
            userIn = input("Enter command (reset): ")
            if userIn == "reset":
                try:
                    rtde_d = dashboard_client(ROBOT_IP, port = 29999, verbose = False)
                    rtde_d.unlockProtectiveStop()
                    print("Protective stop cleared. Returning to idle state.")
                    sm.changeState(idleState())
                    break
                except Exception as e:
                    print(f"Error resetting protective stop: {e}")
            else:
                print("Invalid command. Please type 'reset' to continue.")
    def Exit(self):
        pass

class analyzeState(state):

    def Enter(self):
        print("WE ARE NOW IN ANALYZESTATE")
        print("moveState: bevæger mod home:")
        moveRobot.move_to_target(stateValues.home_pose)
        self.Run() 

    def Run(self):
        # Call the new function in detectObject
        best_target_pose, target_depot = detectObject.run_detection()

        if best_target_pose and target_depot:
            print("best target pose from vision:", best_target_pose)
            print("target depot from vision:", target_depot)
            # Gem best_target_pose på statemachine, så moveState kan bruge det
            stateValues.target_pose = best_target_pose
            stateValues.target_depot = target_depot
            print("stateValue", stateValues.target_pose)
            print("stateValue depot", stateValues.target_depot)
            sm.changeState(moveState())
        else:
            print("Ingen objekt fundet. eller intet target depot")
            sm.changeState(idleState())
        
    def Exit(self):
        pass

if __name__ == "__main__":
    sm = stateMachine(idleState())
    sm.run()