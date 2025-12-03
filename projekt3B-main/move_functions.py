import rtde_receive
import rtde_control
import time
import cv2
import numpy as np
import depthai as dai


def getControlConnection(robot_ip):
    conn = rtde_control.RTDEControlInterface(robot_ip)
    return conn

def getRecieveConnection(robot_ip):
    rec_conn = rtde_receive.RTDEReceiveInterface(robot_ip)
    return rec_conn

def moveRobot(conn, targetPose):
    print("Target TCP pose:", targetPose)
    conn.moveL(targetPose, 0.25, 0.5)  # her i moveL der sætter vi speed og accleartion
    time.sleep(0.5)
    conn.stopScript()
    print(f"Command Move to: {targetPose} Sent to Robot")

def getCurrentPose(rec_conn):
    currentPose = rec_conn.getActualTCPPose()
    return currentPose

def useGripper(conn, width:float, force):
    conn.sendCustomScript("rg2_init()")
    conn.sendCustomScript(f"rg_grip({width},{force})")


