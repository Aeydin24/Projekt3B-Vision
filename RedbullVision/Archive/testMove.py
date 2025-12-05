#!/usr/bin/env python3
#Brug det her script til at flytte robotten til en lokation baseret på et rødt objekts position i billedet.
import time

import cv2
import depthai as dai
import numpy as np
import rtde_control
import rtde_receive
ROBOT_IP = "192.168.0.2"

def test():
    Z_FIXED = 0.01
    rtde_c = rtde_control.RTDEControlInterface(ROBOT_IP)
    rtde_r = rtde_receive.RTDEReceiveInterface(ROBOT_IP)
    print(f"Connected to UR3e at {ROBOT_IP}")

    # Get current TCP pose and build target pose
    tcp_pose = rtde_r.getActualTCPPose()
    print("Current TCP pose:", tcp_pose)

    #her har vi den her liste gruden til at fordi ligenu får vi ikke vores rotations matrix. så der får tager vi
    # vores current tcp position fra robten så bagefter ændre vi bare de 3 første værdier i arrayet så vores nu værneede
    # rotation på tcp ikke ændre sig vi kan altid bare tilføje vores egen rotation hvis vi vil men eller altid bare 
    # sætte den så den altid peget nedad det må vi lige finde ud af.
    while True:
        target_pose = list(tcp_pose)
        target_pose[0] = 0.2098560205445687
        target_pose[1] = -0.293125853083126
        target_pose[2] = Z_FIXED

        print("Target TCP pose:", target_pose)
        print("Moving with moveL...")
        rtde_c.moveL(target_pose, 0.25, 0.5)
        target_pose = list(tcp_pose)
        target_pose[0] = 0.2698560205445687
        target_pose[1] = -0.40125853083126
        target_pose[2] = Z_FIXED
        rtde_c.moveL(target_pose, 0.25, 0.5)
        print("Moving with moveL...")
        target_pose = list(tcp_pose)
        target_pose[0] = 0.2398560205445687
        target_pose[1] = -0.20125853083126
        target_pose[2] = Z_FIXED
        print("Target TCP pose:", target_pose)
        rtde_c.moveL(target_pose, 0.25, 0.5)


if __name__ == "__main__":
    test()