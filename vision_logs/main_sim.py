# main.py
import Utilities
from StateMachine import Machine
from kim_States import idleState

if __name__ == "__main__":

    # Start kameraet
    Utilities.initCamera()

    # Start statemachine
    system = Machine("visionSystem", idleState())

    # Giv videoQueue til systemet
    system.videoQueue = Utilities._videoQueue

    # Kør state machine
    system.run()
