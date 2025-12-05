import asyncio
from stateMachine import stateMachine,state
import detectObject
import moveRobot
import camPipeline
import threading
startStream = False
class idleState(state):
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
        # Hent target_pose fra statemachine (sat i analyzeState)
        target_pose = self.stateMachine.target_pose
        if target_pose is None:
            print("moveState: ingen target_pose fundet – tilbage til idle.")
            self.stateMachine.changeState(idleState())
            return

        print("moveState: bevæger mod target:", target_pose)
        moveRobot.move_to_target(target_pose)

        # Når vi er færdige med at flytte, gå tilbage til idle
        self.stateMachine.changeState(idleState())

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
        self.best_target_pose = None
        print("enter analyzeState:", self.best_target_pose)
        self.Run() 

    def Run(self):
        print("Running vision analysis...")
        # Call the new function in detectObject
        self.best_target_pose = detectObject.run_detection()
        print("best target pose from vision:", self.best_target_pose)

        if self.best_target_pose:
            # Gem best_target_pose på statemachine, så moveState kan bruge det
            self.stateMachine.target_pose = self.best_target_pose
            print("Skifter til moveState med target_pose.")
            self.stateMachine.changeState(moveState())
        else:
            print("Ingen objekt fundet.")
            self.stateMachine.changeState(idleState())
        

if __name__ == "__main__":
    stateMachine(idleState()).run()
