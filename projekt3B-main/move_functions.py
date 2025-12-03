import rtde_receive
import rtde_control
import time
import cv2
import numpy as np
import depthai as dai
import onRobot.gripper as gripper

def getConnection(robot_ip):
    conn = rtde_control.RTDEControlInterface(robot_ip)
    return conn

def moveRobot(conn, targetPose):
    print("Target TCP pose:", targetPose)
    conn.moveL(targetPose, 0.25, 0.5)  # her i moveL der sætter vi speed og accleartion
    time.sleep(0.5)
    conn.stopScript()
    print("Command Sent to Robot")

def getCurrentPose(rec_conn):
    currentPose = rec_conn.RTDEReceiveInterface.getActualTCPPose()
    return currentPose

def useGripper(robot_ip, width, force):
    rgg = gripper.RG2(robot_ip)
    rgg.rg_grip(width, force)


