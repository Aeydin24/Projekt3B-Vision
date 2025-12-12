from StateMachine import StateMachine,State
import cv2
import vision as vi

class idleState(State):
    

    def Run(self):
        print()
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
        
           
    def Run(self):

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

    def Enter(self):
        self.result = []
        print("enter state:", self.result)
        self.Run() 

    def Run(self):
        if  not self.result:
            print("Running vision analysis...")
            self.result = vi.main()
            print("Result after tcp:", self.result)
            if self.result:
                print("Result already obtained:", self.result)
                self.stateMachine.changeState(idleState())
        else:
            print("Could be old result", self.result)
            self.stateMachine.changeState(idleState())
        
        


def main():
    
    pass


if __name__ == "__main__":
    StateMachine(idleState()).run()

    main()