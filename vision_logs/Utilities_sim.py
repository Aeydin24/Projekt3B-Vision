#Utilities_sim.py

import numpy as np

# ---------- DROP OFF POSITIONS ----------
DROP_OFF_POINTS = {
    "red":    (0.20, -0.30, 0.25),
    "green":  (0.25, -0.30, 0.25),
    "yellow": (0.30, -0.30, 0.25)
}

def getDropOffPosition(color):
    return DROP_OFF_POINTS.get(color, (0.20, -0.20, 0.25))


# ---------- SIMULATED ROBOT POSITION ----------
sim_robot_pose = [0.0, 0.0, 0.25]   # x, y, z


# ---------- FAKE pixel_to_world ----------

def pixel_to_world(px, py):
    # Ekstremt simpel mapping til test
    return px/1000.0, py/1000.0


# ---------- SIM MOVE: object movement ----------
def moveTo_sim(target):

    global sim_robot_pose

    wx, wy = pixel_to_world(target["x"], target["y"])
    wz = 0.25

    rx, ry, rz = sim_robot_pose

    dx = wx - rx
    dy = wy - ry
    dz = wz - rz

    # Simuler små bevægelser
    step = 0.01
    mx = np.clip(dx, -step, step)
    my = np.clip(dy, -step, step)
    mz = np.clip(dz, -step, step)

    sim_robot_pose[0] += mx
    sim_robot_pose[1] += my
    sim_robot_pose[2] += mz

    print(f"[SIM MOVE] Robot now at {sim_robot_pose}")

    return abs(dx) < 0.005 and abs(dy) < 0.005


# ---------- SIM MOVE: dropoff movement ----------
def moveToColorSpot_sim(dropTarget):

    global sim_robot_pose

    tx, ty, tz = dropTarget
    rx, ry, rz = sim_robot_pose

    dx = tx - rx
    dy = ty - ry
    dz = tz - rz

    step = 0.01
    mx = np.clip(dx, -step, step)
    my = np.clip(dy, -step, step)
    mz = np.clip(dz, -step, step)

    sim_robot_pose[0] += mx
    sim_robot_pose[1] += my
    sim_robot_pose[2] += mz

    print(f"[SIM DROP] Robot now at {sim_robot_pose}")

    return abs(dx) < 0.005 and abs(dy) < 0.005
