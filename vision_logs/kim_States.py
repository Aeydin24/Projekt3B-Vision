# kim_States.py
from StateMachine import State
import Utilities, Utilities_sim, cv2
from Utilities import getVideo   



# -----------------------------------------
# IDLE
# -----------------------------------------
class idleState(State):
    def Run(self):
        user = input("Enter command (start/quit): ")

        if user.lower() == "start":
            print("[STATE] Switching to AnalyzeState")
            return AnalyzeState()

        if user.lower() == "quit":
            print("[SYSTEM] Shutdown requested")
            exit()

        print("Unknown command")
        return self


# -----------------------------------------
# ANALYZE
# -----------------------------------------
class AnalyzeState(State):
    def Run(self):
        # Hvis i sim-mode, spring kamera over // slettes senere
        if self.stateMachine.videoQueue is None:
            print("SIM MODE: Analyzer springer kamera over")
            return self
        #-----------------------------------
        # Hent ét frame fra kamera
        frame = Utilities.getVideo()

        cv2.imshow("Vision Feed", frame)
        cv2.waitKey(1)


        if frame is None:
            print("[ERROR] No frame from camera")
            return self

        # Analyser frame for objekterstep

        detected = Utilities.analyzeFrame(frame)

        if detected:
            print(f"[VISION] Found {len(detected)} objects")
            self.stateMachine.objectsDetected = detected
            return MoveState()

        # Hvis ingen objekter → fortsæt analyze
        return self


# -----------------------------------------
# MOVE
# -----------------------------------------




class MoveState(State):

    def Run(self):


        if self.stateMachine.rtde_c is None:
            print("[MOVE] Ingen robot — hopper tilbage til Analyze")
            return AnalyzeState()

        if not self.stateMachine.objectsDetected:
            print("[MOVE] Ingen objekter – tilbage til Analyze")
            return AnalyzeState()

        obj = self.stateMachine.objectsDetected.pop(0)

        shape = obj["shape"]
        x = obj["x"]
        y = obj["y"]
        color = obj["color"]

        print(f"[MOVE] Behandler objekt: {shape}, farve: {color}, pos: ({x}, {y})")

        # SIM MODE
        if self.stateMachine.videoQueue is None:
            print(f"[SIM] Robotten ville flytte {color}-objektet til drop-off position")
            return AnalyzeState()

        # REAL MODE
        print("[REAL] Flytter objekt på UR robot...")

        self.stateMachine.rtde_c.moveL([x, y, 0.2, 0, 0, 0], 0.2, 0.2)
        self.stateMachine.rtde_c.moveL([x, y, 0.05, 0, 0, 0], 0.2, 0.2)

        print("[REAL] Objekt flyttet – tilbage til AnalyzeState")
        return AnalyzeState()


# -----------------------------------------
# ERROR STATE  (kan udvides senere)
# -----------------------------------------
class ErrorState(State):
    def Run(self):
        print("[ERROR] Something went wrong")
        return idleState()


