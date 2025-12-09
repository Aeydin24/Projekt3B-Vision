import rtde_control
import rtde_receive
import rtde_io
import time
from stateMachine import stateValues

ROBOT_IP = "192.168.0.2"

rtde_c = rtde_control.RTDEControlInterface(ROBOT_IP)
rtde_r = rtde_receive.RTDEReceiveInterface(ROBOT_IP)
rtde_i = rtde_io.RTDEIOInterface(ROBOT_IP)

# note til mig selv måske skal vi vi lave listen om på traget_pose osv i vores move så vi ikke behøver at have sådan mange andre steder, det gør det nemmere da vi aldrig vil bruge vores rotations axis
def move_to_target(target_pose, fixed_height=False):
    target = list(target_pose) #kopi
    if target is None:
        print("moveRobot: No target pose provided.")
        return
    elif fixed_height:
        target[2] = stateValues.home_pose[2]  
    try:
        current_pose = getCurrentPose()
        target[3] = current_pose[3]
        target[4] = current_pose[4]
        target[5] = current_pose[5]
        rtde_c.moveL(target, 0.25, 0.5)
        #lav exception til forskellige states fra robotten fx. protective stop osv.
    except Exception as e:
        print(f"moveRobot: Error during movement: {e}")

#vi kan selv styre vores stop forxemple hvis vi bruger yolo til hånd så skal den stoppe hårdt, hvis det bare er normal stop så kan det være blødt
def closeGripper():
    #if not rtde_r.getDigitalOutState(16):
        rtde_i.setToolDigitalOut(0, True)
        time.sleep(1)
    #else:
        #print("Gripper is already closed!")

def openGripper():
    #if rtde_r.getDigitalOutState(16):
        rtde_i.setToolDigitalOut(0, False)
        time.sleep(1)
    #else:
        #print("Gripper is already open!")

def getCurrentPose():
    currentPose = rtde_r.getActualTCPPose()
    return currentPose