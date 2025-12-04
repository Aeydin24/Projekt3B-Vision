# StateMachine_sim.py
import time

class visionSystem_sim:
    def __init__(self, state):
        self.rtde_c = None
        self.rtde_r = None
        self.videoQueue = None
        self.objectsDetected = []
        self.state = state
        self.state.stateMachine = self

    def run(self):
        while True:
            self.state = self.state.Run()
            self.state.stateMachine = self
            time.sleep(0.1)
