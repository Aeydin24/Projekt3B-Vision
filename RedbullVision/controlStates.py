import asyncio
from stateMachine import stateMachine,state
import detectObject
import moveRobot
import camPipeline
import threading
startStream = False
class idleState(state):
    def Enter(self):
        print("WE ARE NOW IN IDLESTATE ")
        self.Run()
    def Run(self):
        global startStream
        if startStream == False:
            asyncCam = threading.Thread(name='image_capture', target=camPipeline.image_capture)
            asyncCam.start()
            startStream = True        
        userIn = input("Enter a command (start/move): ")
        if userIn == "start":
            self.stateMachine.changeState(analyzeState()) 
        elif userIn == "move":
            self.stateMachine.changeState(moveState())
            stateMachine(idleState())
        else:
            print("Invalid command")
            self.stateMachine.changeState(idleState())

    # skriv at du er i idle state hvert 10 sekund
    # if start command received, change to analyseState

class moveState(state):
    def Enter(self):
        print("WE ARE NOW IN MOVESTATE ")
        self.Run()

    def Run(self):
        # Hent target_pose og alt de ander fra statemachine (sat i analyzeState)
        target_pose = self.stateMachine.target_pose
        target_depot = self.stateMachine.target_depot
        home_pose = self.stateMachine.home_pose
        fixed_height = True 
        print("moveState: åbner gripper")
        moveRobot.openGripper()
        print("moveState: bevæger mod target:", target_pose)
        moveRobot.move_to_target(target_pose, fixed_height)
        moveRobot.move_to_target(target_pose)
        print("moveState: bevæger mod home:", home_pose)
        moveRobot.move_to_target(home_pose)
        print("moveState: lukker gripper")
        moveRobot.closeGripper()
        print("moveState: bevæger mod depot:", target_depot)
        moveRobot.move_to_target(target_depot)
        print("moveState: åbner gripper")
        moveRobot.openGripper()
        print("moveState: bevæger mod home:", home_pose)
        moveRobot.move_to_target(home_pose)
        # Når vi er færdige med at flytte, gå tilbage til idle
        self.stateMachine.changeState(analyzeState())

    def Exit(self):
        pass


class errorState(state):
    def Enter(self):

        pass   
    
    def Run(self):
        
        pass

    def Exit(self):
        pass

class analyzeState(state):

    def Enter(self):
        print("enter analyzeState:")
        self.Run() 

    def Run(self):
        print("Running vision analysis...")
        # Call the new function in detectObject
        best_target_pose, target_depot = detectObject.run_detection()
        print("best target pose from vision:", best_target_pose)
        print("target depot from vision:", target_depot)

        if best_target_pose and target_depot:
            # Gem best_target_pose på statemachine, så moveState kan bruge det
            self.stateMachine.target_pose = best_target_pose
            self.stateMachine.target_depot = target_depot
            print("Skifter til moveState med target_pose. og target_depot")
            self.stateMachine.changeState(moveState())
        else:
            print("Ingen objekt fundet. eller intet target depot")
            self.stateMachine.changeState(idleState())
        

if __name__ == "__main__":
    stateMachine(idleState()).run()
