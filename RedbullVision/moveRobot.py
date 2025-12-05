import rtde_control
import rtde_receive
import time

ROBOT_IP = "192.168.0.2"

def move_to_target(target_pose):
    if target_pose is None:
        print("moveRobot: No target pose provided.")
        return

    try:
        rtde_c = rtde_control.RTDEControlInterface(ROBOT_IP)
        rtde_r = rtde_receive.RTDEReceiveInterface(ROBOT_IP)
        current_pose = rtde_r.getActualTCPPose()
        print(f"moveRobot: Connected to robot at {ROBOT_IP}")
        print(f"moveRobot: From to {current_pose}")
        print(f"moveRobot: Moving to {target_pose}")
        # moveL(pose, speed, acceleration)
        rtde_c.moveL(target_pose, 0.25, 0.5)
        
        print("moveRobot: Movement complete.")
        
    except Exception as e:
        print(f"moveRobot: Error during movement: {e}")
