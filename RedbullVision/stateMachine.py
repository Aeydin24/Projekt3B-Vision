class state:
    stateMess = None
    def Enter(self):
        self.stateMess = "Entering"
        print(f"Entering state: {self.__class__.__name__}")
        self.Run()
        
    def Run(self):
        self.stateMess = "Running"
        print(f"Running state: {self.__class__.__name__}")
        
    def Exit(self):
        self.stateMess = "Exiting"
        print(f"Exiting state: {self.__class__.__name__}")
    
    def getState(self):
        return self.stateMess
    

class stateMachine:

    def __init__(self, state:state):
        self.target_pose = None
        self.target_depot = None
        self.home_pose = [-0.009, -0.30698, 0.2]
        self.state = state
        self.state.stateMachine = self
        
    def changeState(self, newstate:state):
        self.state = self.state.Exit()
        self.state = newstate

        self.state.stateMachine = self
        self.state.Enter()
        
    def run(self):
        self.state.Enter()
        self.running = True
        while self.running:
            self.state = self.state.Run()

