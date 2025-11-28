# MyStateMachine.py


class State:
    stateMess = None
 
    def Enter(self):   # kaldes én gang når state aktiveres
        self.stateMess = "Entering state :"
        print(f"{self.stateMess} : {self.__class__.__name__}")

    def Run(self):     # kaldes gentagne gange mens state er aktiv
        self.stateMess = "Running State :"
        print(f"{self.stateMess}: {__class__.__name__}")

    def Exit(self):    # kaldes lige før state forlades
        self.stateMess = "Exiting State : {__class__.__name__}"
    def GetState(self):
        
        return self.stateMess
    
class StateMachine:
    def __init__(self, state: State):
        self.state = state          # aktiv state (instance)
        self.state.machine = self   # gør maskinen synlig for state

    def ChangeState(self, new_state: State):
        # forventer en *instance* (fx GreenState()), ikke en klasse
        self.state.Exit()           # kald Exit på gammel state
        self.state = new_state      # skift reference til ny state
        self.state.machine = self   # sæt maskine på ny state
        self.state.Enter()          # kald Enter én gang     
        
    def Run(self):
        self.running = True
        while self.running:
            self.state.Run()