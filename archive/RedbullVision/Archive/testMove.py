#!/usr/bin/env python3
#Brug det her script til at flytte robotten til en lokation baseret på et rødt objekts position i billedet.
import time

import cv2
import depthai as dai
import numpy as np
import rtde_control
import rtde_receive
import rtde_io

ROBOT_IP = "192.168.1.28"
rtde_r = rtde_receive.RTDEReceiveInterface(ROBOT_IP)
rtde_c = rtde_control.RTDEControlInterface(ROBOT_IP)
rtde_i = rtde_io.RTDEIOInterface(ROBOT_IP)

print(f"Connected to robot at {ROBOT_IP}")


def test():
    global rtde_r, rtde_c, rtde_i
    while True:    
        time.sleep(1)
        print("im in while TRUE1")
        print("im in while TRUE2")
        if rtde_r.isConnected() == False:
            print("this is under isConnected false")
            try:
                print("Attempting to connect to UR3e...")            
                rtde_r.reconnect()
                rtde_c.reconnect()
                rtde_i.reconnect()
                print(f"Connected to UR3e at {ROBOT_IP}")

                
            except Exception as e:
                print(f"Connection failed: {e}. Retrying in 2 seconds...")
            





if __name__ == "__main__":
    test()