from StateMachine import State
import Utilities_sim

class idleState_sim(State):
    def Run(self):
        print("[SIM] idle → analyze")
        return AnalyzeState_sim()


class AnalyzeState_sim(State):
    def Run(self):
        print("[SIM] Analyzer finder 1 fake objekt")
        fake_object = {"x": 200, "y": 150, "color": "red"}
        self.stateMachine.objectsDetected = [fake_object]
        return MoveState_sim()


class MoveState_sim(State):
    def Run(self):
        obj = self.stateMachine.objectsDetected.pop(0)
        print(f"[SIM] Flytter objekt {obj}")

        reached = Utilities_sim.moveTo_sim(obj)

        if reached:
            drop = Utilities_sim.getDropOffPosition(obj["color"])
            Utilities_sim.moveToColorSpot_sim(drop)
            print(f"[SIM] Objekt droppet ved {drop}")
            return AnalyzeState_sim()

        return self
