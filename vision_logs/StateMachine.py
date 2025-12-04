#StateMachine.py

from rtde_control import RTDEControlInterface
from rtde_receive import RTDEReceiveInterface




class State:
    stateMess = None
    def Enter(self):
        self.stateMess = "Entering"
        print(f"Entering state: {self.__class__.__name__}")
        
    def Run(self):
        self.stateMess = "Running"
        print(f"Running state: {self.__class__.__name__}")
        
    def Exit(self):
        self.stateMess = "Exiting"
        print(f"Exiting state: {self.__class__.__name__}")
    
    def getState(self):
        return self.stateMess

class StateMachine:

    def __init__(self, state:"State"):
        self.state = state
        self.state.stateMachine = self
        self.previousState = None
       


    def changeState(self, newstate:"State"):
        self.previousState = self.__class__.__name__
        self.state = self.state.Exit()
        self.state = newstate

        self.state.stateMachine = self
        self.state.Enter()
        
    def run(self):
        self.state.Enter()
        self.running = True
        while self.running:
            new_state = self.state.Run()

            if new_state is not self.state:
                self.state.Exit()
                self.state = new_state
                self.state.stateMachine = self
                self.state.Enter()
            else:
                self.state = new_state



class Machine(StateMachine):
    def __init__(self, name,state:"State"):
        super().__init__(state)
        self.name = name
#----------------------------------------------



class visionSystem(Machine):

    def __init__(self, state:"State"):
        super().__init__("visionSystem", state)

        self.targetPos = []
        self.currentPos = []
        self.objectsDetected = []
        self.HomePos = []
        self.videoQueue = None

        # ur kommunikation
        ROBOT_IP = "192.168.0.2"
        FREQUENCY = 500

        try:
            self.rtde_c = RTDEControlInterface(ROBOT_IP, FREQUENCY)
            self.rtde_r = RTDEReceiveInterface(ROBOT_IP, FREQUENCY)
        except:
            print("[WARN] Robot ikke forbundet. Kører vision-only mode.")
            self.rtde_c = None
            self.rtde_r = None

        self.dt = 1.0 / FREQUENCY
        self.max_xy_step = 0.002
