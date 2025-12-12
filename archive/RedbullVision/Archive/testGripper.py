import rtde_control
import rtde_io
import time

ROBOT_IP = "192.168.0.2"

def main():
        rtde_i = rtde_io.RTDEIOInterface(ROBOT_IP)
        rtde_c = rtde_control.RTDEControlInterface(ROBOT_IP)
        print(f"moveRobot: Connected to robot at {ROBOT_IP}")
        time.sleep(1)  # wait for the gripper to open

        #rtde_c.sendCustomScript("rg2_open()")
        #rtde_c.sendCustomScript("rg_grip(rg_width = 10, force =10, tool_index=0, blocking=True, depth_compensation=False, popupmsg=True)")
        #rtde_c.sendCustomScript("rg_grip(10, 10, tool_index=0, blocking=True, depth_compensation=False, popupmsg=True)")
        #rtde_c.sendCustomScript("rg2_move(110, 40, 0, false)")

        rtde_i.setToolDigitalOut(0, True)  # Open gripper
        time.sleep(3)  # wait for the gripper to open
        print("moveRobot: Movement complete.")
        rtde_c.stopScript()

if __name__ == "__main__":
    main()