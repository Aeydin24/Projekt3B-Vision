import time

import vision_functions as vf
import move_functions as mf
from StateMachine import StateMachine, State, Objects
import cv2
import numpy as np
import rtde_control
import rtde_receive
import onRobot.gripper as gripper


# noinspection PyUnresolvedReferences
class idleState(State):

    def Run(self):
        userIn = input("Enter a command (start/quit): ")
        if userIn == "quit":
            exit(0)
        elif userIn == "start":
            sm.changeState(analyzeState())
        else:
            print("Invalid command")
            sm.changeState(idleState())

class analyzeState(State):

    def Run(self):
        # Init af robotÍP, pixelværdier og deres korresponderende punkter i 3D space.
        robot_ip = "192.168.0.2"
        image_points = np.array([
            [269.20438, 231.23853],

            [282.9418, 231.40858],

            [296.31116, 231.70386],

            [309.9476, 232.38803],

            [323.8921, 232.57532],

            [337.60565, 232.75604],

            [351.3533, 233.22455],

            [365.01834, 233.60591],

            [378.67422, 233.7799],

            [268.841, 244.78584],

            [282.4767, 245.30753],

            [296.24783, 245.46617],

            [309.68488, 245.74896],

            [323.53073, 246.2915],

            [337.2779, 246.68903],

            [350.79984, 247.12007],

            [364.67224, 247.39052],

            [378.59515, 247.61728],

            [268.43887, 258.54147],

            [282.13168, 258.77237],

            [295.53882, 259.06018],

            [309.52545, 259.63516],

            [323.3153, 260.05283],

            [336.7843, 260.45132],

            [350.52014, 260.5951],

            [364.50082, 260.87234],

            [378.23056, 261.40582],

        ], dtype=np.float32)
        world_points_3d = np.array([
            [0.2098560205445687, -0.293125853083126, 0.013670630725627242],
            [0.209401954589718, -0.2711256346025363, 0.013327877648154018],
            [0.20906502743724822, -0.24926116182991437, 0.012543638832057252],
            [0.20886240887486554, -0.2271302512621807, 0.012373404279126837],
            [0.20848766396196963, -0.20496313139630995, 0.012252829778616692],
            [0.20817273788347945, -0.1833259801173631, 0.012114139819924513],
            [0.20799476694021798, -0.16106631569378776, 0.011995707524490473],
            [0.207554489730145, -0.13910713469294328, 0.011871996935032408],
            [0.20717687477421276, -0.11687377850645889, 0.011677309991467183],
            [0.2313415527416441, -0.2928574327410153, 0.013715861589905759],
            [0.23138952164952167, -0.27047358878534444, 0.01348850467954757],
            [0.23091004698025958, -0.24878923358197233, 0.01308993966585642],
            [0.2305819127654663, -0.22668289622554644, 0.012725113441341501],
            [0.23011073131476434, -0.20464560686009842, 0.012684423402256478],
            [0.2301156497310216, -0.18285351131535602, 0.012497146266276904],
            [0.22987321764270285, -0.16080497669021565, 0.012233394577078532],
            [0.22921479477099643, -0.13865024288466585, 0.011873158813579088],
            [0.2293125978978605, -0.11655679055724535, 0.01195326730542165],
            [0.25346812705447275, -0.292586145697203, 0.014110253289649821],
            [0.25332253282965933, -0.27032362248368796, 0.013643912310361911],
            [0.2530193077137687, -0.24821718364583117, 0.01357129172604421],
            [0.2525028388694907, -0.226512226207693, 0.012994836393279308],
            [0.25232225737581687, -0.2042546586583563, 0.013091883638745583],
            [0.2521291762231683, -0.18194358434045882, 0.012694146761365294],
            [0.251566597211971, -0.1599515597186626, 0.012447728266800878],
            [0.2515184408421431, -0.13816584516870278, 0.012483650489861761],
            [0.25077065872364485, -0.1162147352399853, 0.0121665226592364]
        ], dtype=np.float32)
        # Slicing af kun de to første værdier i hvert world point (x,y) i 3D space
        world_points = world_points_3d[:, :2]
        # Udregning af homografi for billede planet og 3D planet
        H, _ = cv2.findHomography(image_points, world_points)
        # Fast Z punkt i 3D space
        z_fixed = 0.05
        # Init af bgr videofeed
        frame = vf.create_bgr_pipeline()
        time.sleep(5)
        center_point = vf.find_red_center(frame)
        targetPose = vf.print_target_pose(center_point ,robot_ip, z_fixed, H)
        sm.targetPose = targetPose
        self.Exit()

    def Exit(self):
        print("Exiting analyseState...")
        sm.changeState(moveState())

class moveState(State):

    def Run(self):
        robot_ip = "192.168.0.2"
        conn = mf.getConnection(robot_ip)
        currentPose = mf.getCurrentPose(rtde_receive)
        mf.moveRobot(conn, sm.targetPose)

        while currentPose != sm.targetPose:
            print("Moving to target pose...")
            time.sleep(1)

        # Grib om emne her
        mf.useGripper(robot_ip, 30, 40)
        # Skift targetPose til ny pose
        sm.targetPose = []
        # Kør mod sorteringsplads
        mf.moveRobot(conn, sm.targetPose)
        # Slip emne
        mf.useGripper(robot_ip, 0, 0)
        sm.changeState(idleState())

    def Exit(self):
        pass


class errorState(State):
    def Enter(self):
        pass

    def Run(self):
        pass

    def Exit(self):
        pass


if __name__ == "__main__":
    sm = StateMachine(idleState())
    sm.run()
