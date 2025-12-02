#!/usr/bin/env python3
import time

import cv2
import numpy as np
import rtde_control
import rtde_receive


ROBOT_IP = "192.168.0.2"
ROBOT_FREQUENCY = 500  # Hz


def main():
	rtde_c = rtde_control.RTDEControlInterface(ROBOT_IP, ROBOT_FREQUENCY)
	rtde_r = rtde_receive.RTDEReceiveInterface(ROBOT_IP, ROBOT_FREQUENCY)
	print(f"Connected to UR3e at {ROBOT_IP}")

	dt = 1.0 / ROBOT_FREQUENCY

	# step sizes (meters for XYZ, radians for rotations)
	step_xy = 0.05
	step_z = 0.05
	step_rot = np.deg2rad(1.0)

	print("Manual control:")
	print("  W/S: X +/-,  A/D: Y +/-,  E/Q: Z +/-")
	print("  Arrow Up/Down: RX +/-,  Arrow Left/Right: RY +/-")
	print("  ESC or 'x' to exit")

	# simple black window just to capture key events
	window_name = "Robot Manual Control (focus here, use keys)"
	cv2.namedWindow(window_name)
	img = np.zeros((200, 600, 3), dtype=np.uint8)

	running = True
	while running:
		img[:] = 0
		cv2.putText(
			img,
			"W/S: X  A/D: Y  E/Q: Z  Arrows: RX/RY",
			(10, 30),
			cv2.FONT_HERSHEY_DUPLEX,
			0.6,
			(255, 225, 255),
			2,
		)
		cv2.putText(
			img,
			"ESC or X to quit",
			(10, 180),
			cv2.FONT_HERSHEY_DUPLEX,
			0.4,
			(70, 50, 255),
			1,
		)
		cv2.putText(
			img,
			tcp_pose_str := f"TCP Pose: {np.array2string(np.array(rtde_r.getActualTCPPose()), precision=3, suppress_small=True)}",
			(10, 100),
			cv2.FONT_HERSHEY_DUPLEX,
			0.6,
			(255, 225, 255),
			1,
		)

		cv2.imshow(window_name, img)
		key = cv2.waitKey(int(dt * 1000)) & 0xFF

		# get current pose each cycle
		tcp_pose = list(rtde_r.getActualTCPPose())

		# linear movement
		if key == ord("w"):
			tcp_pose[0] += step_xy
		elif key == ord("s"):
			tcp_pose[0] -= step_xy
		elif key == ord("a"):
			tcp_pose[1] += step_xy
		elif key == ord("d"):
			tcp_pose[1] -= step_xy
		elif key == ord("e"):
			tcp_pose[2] += step_z
		elif key == ord("q"):
			tcp_pose[2] -= step_z

		# rotation (rx, ry) with arrow keys
		elif key == 82:  # up arrow
			tcp_pose[3] += step_rot
		elif key == 84:  # down arrow
			tcp_pose[3] -= step_rot
		elif key == 81:  # left arrow
			tcp_pose[4] += step_rot
		elif key == 83:  # right arrow
			tcp_pose[4] -= step_rot

		# exit on ESC or 'x'
		elif key == 27 or key == ord("x"):
			running = False

		# send servoL command only if some key was pressed (non -1)
		if key != 255 and key != -1:
			rtde_c.servoL(
				tcp_pose,
				0.25,  # speed
				0.5,   # acceleration
				dt,
				0.1,   # lookahead time
				300,   # gain
			)
			print("TCP pose:", tcp_pose)

		# small sleep to keep timing stable
		time.sleep(dt)

	cv2.destroyAllWindows()
	rtde_c.stopScript()
	print("Manual control finished.")


if __name__ == "__main__":
	main()

