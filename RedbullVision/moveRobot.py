import rtde_control
import rtde_receive
import rtde_io
import time
homePos= [-0.009, -0.30698, 0.2]

ROBOT_IP = "192.168.0.2"
rtde_c = rtde_control.RTDEControlInterface(ROBOT_IP)
rtde_r = rtde_receive.RTDEReceiveInterface(ROBOT_IP)
rtde_i = rtde_io.RTDEIOInterface(ROBOT_IP)


def move_to_target(target_pose):
    if target_pose is None:
        print("moveRobot: No target pose provided.")
        return

    try:
        current_pose = rtde_r.getActualTCPPose()
        print(f"moveRobot: Connected to robot at {ROBOT_IP}")
        print(f"moveRobot: From to {current_pose}")
        print(f"moveRobot: Moving to {target_pose}")
        # moveL(pose, speed, acceleration)
        rtde_c.moveL(target_pose, 0.25, 0.5)
        print("moveRobot: Movement complete.")
        #lav exception til forskellige states fra robotten fx. protective stop osv.
    except Exception as e:
        print(f"moveRobot: Error during movement: {e}")


def stop_movement():
    try:
        rtde_c = rtde_control.RTDEControlInterface(ROBOT_IP)
        rtde_c.stopL()
        print("moveRobot: Movement stopped.")
    except Exception as e:
        print(f"moveRobot: Error stopping movement: {e}")

def closeGripper():
    if not rtde_r.getDigitalOutState(16):
        rtde_i.setToolDigitalOut(0, True)
        time.sleep(1)
    else:
        print("Gripper is already closed!")

def openGripper():
    if rtde_r.getDigitalOutState(16):
        rtde_i.setToolDigitalOut(0, False)
        time.sleep(1)
    else:
        print("Gripper is already open!")

#Her kan vi parse home og depot positions fra controlStates 
def home_location(homePos):
    try:
        rtde_c = rtde_control.RTDEControlInterface(ROBOT_IP)
        rtde_r = rtde_receive.RTDEReceiveInterface(ROBOT_IP)
        current_pose = rtde_r.getActualTCPPose()
        print(f"moveRobot: From to {current_pose}")
        print(f"moveRobot: Moving to home position: {homePos}")
        rtde_c.moveL(homePos, 0.25, 0.5)
        print("moveRobot: Reached home position.")
    except Exception as e:
        print(f"moveRobot: Error moving to home position: {e}")

def depot_position(depot_pose):
    try:
        rtde_c = rtde_control.RTDEControlInterface(ROBOT_IP)
        rtde_r = rtde_receive.RTDEReceiveInterface(ROBOT_IP)
        current_pose = rtde_r.getActualTCPPose()
        print(f"moveRobot: From to {current_pose}")
        print(f"moveRobot: Moving to depot position: {depot_pose}")
        rtde_c.moveL(depot_pose, 0.25, 0.5)
        print("moveRobot: Reached depot position.")
    except Exception as e:
        print(f"moveRobot: Error moving to depot position: {e}")