#!/usr/bin/env python3
#Brug det her script til at flytte robotten til en lokation baseret på et rødt objekts position i billedet.
import time
import vision
import rtde_control

ROBOT_IP = "192.168.0.2"

# Fixed Z height in meters
Z_FIXED = 0.05


def main():
    # RTDE robot interfaces
    # Tror godt vi kan fjerne RTDEControlInterface og RTDEReceiveInterface og bare skrive rtde(Robot_ip)
    rtde_c = rtde_control.RTDEControlInterface(ROBOT_IP)
    print(f"Connected to UR3e at {ROBOT_IP}")

    # Vi bruger det samme som fra depthai github eksempler så vi undgår xout osv.
    # igen vi må lige snakke sammen om det her senere jeg syntes vi skal holde det som det er her helt simplet.
    # kunne være fedt hvis der var en der undersøgte om vi kunne sætte fokus på kamera via pipeline.
    print("Target TCP pose:", vision.target_pose)
    print("Moving with moveL...")
    rtde_c.moveL(vision.target_pose, 0.25, 0.5) # her i moveL der sætter vi speed og accleartion
    time.sleep(0.5)


    rtde_c.stopScript()
    print("Done.")


if __name__ == "__main__":
    main()