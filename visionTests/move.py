#!/usr/bin/env python3
#Brug det her script til at flytte robotten til en lokation baseret på et rødt objekts position i billedet.
import time

import cv2
import depthai as dai
import numpy as np
import rtde_control
import rtde_receive

ROBOT_IP = "192.168.0.2"
    
rtde_c = rtde_control.RTDEControlInterface(ROBOT_IP)
