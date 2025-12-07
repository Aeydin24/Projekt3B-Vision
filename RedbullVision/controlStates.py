import asyncio
from stateMachine import stateMachine,state
import detectObject
import moveRobot
from camPipelineV3 import lorteFisseCameaPipeline
import threading


# note til mig selv gør så man kan skriv reboot så vi manualt kan reboot camPipeline tråden
class idleState(state):
    def Enter(self):
        print("WE ARE NOW IN IDLESTATE")
        if not lorteFisseCameaPipeline.initFlag:
            print("Starting camera pipeline thread")
            threading.Thread(name='display frame', target=lorteFisseCameaPipeline.display_frame).start()        
        self.Run()

    def Run(self):
  
        userIn = input("Enter a command (start/vizmode):")
        if userIn == "start":
            self.stateMachine.changeState(analyzeState()) 
        elif userIn == "vizmode":
            lorteFisseCameaPipeline.vizualize = not lorteFisseCameaPipeline.vizualize
            print(f"Vizualize mode set to: {lorteFisseCameaPipeline.vizualize}")
        else:
            print("Invalid command")
            self.stateMachine.changeState(idleState())

    # skriv at du er i idle state hvert 10 sekund
    # if start command received, change to analyseState

class moveState(state):
    def Enter(self):
        print("WE ARE NOW IN MOVESTATE")
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
        print("WE ARE NOW IN ANALYZESTATE")
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
            self.stateMachine.changeState(moveState())
        else:
            print("Ingen objekt fundet. eller intet target depot")
            self.stateMachine.changeState(idleState())
        
    def Exit(self):
        pass

if __name__ == "__main__":
    stateMachine(idleState()).run()
