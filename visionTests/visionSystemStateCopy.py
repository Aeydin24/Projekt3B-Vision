from StateMachine import StateMachine,State
import cv2



class idleState(State):
    

    def Run(self):
        userIn = input("Enter a command (start/move/load/save/quit/velocity): ")
        if userIn == "start":
            self.stateMachine.changeState(analyzeState()) 
        elif userIn == "move":
            self.stateMachine.changeState(moveState())
            StateMachine(idleState())
        else:
            print("Invalid command")
            self.stateMachine.changeState(idleState())


        
        

    # skriv at du er i idle state hvert 10 sekund
    # if start command received, change to analyseState




class moveState(State):
    def Enter(self):
        print("WE ARE NOW IN MOVESTATE ")
        self.Run()
        pass
           
    def Run(self):
        userIn = input("Enter a command (start/move/load/save/quit/velocity): WE ARE NOW IN MOVESTATE ")
        if userIn == "start":
            self.stateMachine.changeState(analyzeState()) 
        elif userIn == "move":
            self.stateMachine.changeState(moveState())
        else:
            print("Invalid command")
            self.stateMachine.changeState(idleState())
        pass

    def Exit(self):
        pass

class errorState(State):
    def Enter(self):

        pass   
    
    def Run(self):

        pass

    def Exit(self):
        pass

class analyzeState(State):

    def Run(self):
    
        pass


def main():
    
    pass


if __name__ == "__main__":
    StateMachine(idleState()).run()

    main()