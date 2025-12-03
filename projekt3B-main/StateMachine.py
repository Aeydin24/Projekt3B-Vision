class State:
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


class StateMachine:

    def __init__(self, state: State):
        self.state = state
        self.state.stateMachine = self
        self.previousState = None

    def changeState(self, newstate: State):
        self.previousState = self.__class__.__name__
        self.state = self.state.Exit()
        self.state = newstate

        self.state.stateMachine = self
        self.state.Enter()

    def run(self):
        self.state.Enter()
        self.running = True
        while self.running:
            self.state = self.state.Run()


class Objects:
    def __init__(self, color: str, shape, px: int, py: int):
        self.color = color
        self.shape = shape
        self.px = px
        self.py = py