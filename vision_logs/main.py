# main.py
import Utilities
from StateMachine import Machine, visionSystem
from kim_States import idleState

if __name__ == "__main__":

    Utilities.initCamera()

    system = visionSystem(idleState())

    system.videoQueue = Utilities._videoQueue

    system.run()

