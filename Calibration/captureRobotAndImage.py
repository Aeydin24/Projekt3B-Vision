import sys
import time
import threading
from pathlib import Path

import numpy as np
import rtde.rtde as rtde
import rtde.rtde_config as rtde_config

import cv2
import depthai as dai

ROBOT_HOST = "192.168.0.2"  # change to your UR3e IP if needed
ROBOT_PORT = 30004
CONFIG_FILE = "record_configuration.xml"
OUTPUT_DIR = Path("captured_poses_npz")
IMAGE_DIR = Path("captured_images")


last_frame_lock = threading.Lock()
last_frame = {"frame": None}


def camera_thread():
    with dai.Pipeline() as pipeline:
        cam = pipeline.create(dai.node.Camera).build()
        videoQueue = cam.requestOutput((640, 480)).createOutputQueue()

        pipeline.start()
        while pipeline.isRunning():
            videoIn = videoQueue.get()
            if videoIn is None:
                continue
            assert isinstance(videoIn, dai.ImgFrame)
            frame = videoIn.getCvFrame()

            # Store latest frame for capture
            with last_frame_lock:
                last_frame["frame"] = frame.copy()

            cv2.imshow("video", frame)
            # Allow UI to update and a way to quit camera window
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cv2.destroyAllWindows()


def next_npz_filename(output_dir: Path) -> Path:
    output_dir.mkdir(exist_ok=True)
    existing = sorted(output_dir.glob("pose_*.npz"))
    if not existing:
        idx = 1
    else:
        last = existing[-1].stem
        try:
            idx = int(last.split("_")[-1]) + 1
        except ValueError:
            idx = 1
    return output_dir / f"pose_{idx:04d}.npz"


def save_pose_npz(timestamp: float, pose):
    path = next_npz_filename(OUTPUT_DIR)

    # Determine matching image path (camera_0001.png etc.)
    IMAGE_DIR.mkdir(exist_ok=True)
    img_name = path.stem.replace("pose_", "camera_") + ".png"
    img_path = IMAGE_DIR / img_name

    # Save pose
    np.savez(path, timestamp=timestamp, pose=np.array(pose, dtype=float))
    print(f"Saved pose to {path}")

    # Grab latest frame from camera thread and save
    with last_frame_lock:
        frame = None if last_frame["frame"] is None else last_frame["frame"].copy()

    if frame is not None:
        cv2.imwrite(str(img_path), frame)
        print(f"Saved image to {img_path}")
    else:
        print("Warning: No camera frame available to save.")


def main():
    # Start camera in background
    cam_t = threading.Thread(target=camera_thread, daemon=True)
    cam_t.start()

    host = ROBOT_HOST
    if len(sys.argv) >= 2:
        host = sys.argv[1]

    conf = rtde_config.ConfigFile(CONFIG_FILE)
    output_names, output_types = conf.get_recipe("out")

    con = rtde.RTDE(host, ROBOT_PORT)
    con.connect()

    if not con.negotiate_protocol_version():
        print("Could not negotiate protocol version with robot")
        con.disconnect()
        return

    con.send_output_setup(output_names, output_types)

    if not con.send_start():
        print("RTDE start failed")
        con.disconnect()
        return

    print(f"Connected to UR robot at {host}")
    print("Streaming TCP pose. Commands:")
    print("  c + Enter  -> capture current TCP to NPZ file")
    print("  q + Enter  -> quit")
    print(f"NPZ files will be stored in folder: {OUTPUT_DIR}")

    running = True
    latest_state = {"timestamp": None, "pose": None}

    def input_thread():
        nonlocal running
        while running:
            try:
                cmd = input().strip().lower()
            except EOFError:
                break

            if cmd == "c":
                if latest_state["pose"] is not None:
                    save_pose_npz(latest_state["timestamp"], latest_state["pose"])
                else:
                    print("No TCP pose available yet to capture.")
            elif cmd == "q":
                print("Quit command received.")
                running = False

    t = threading.Thread(target=input_thread, daemon=True)
    t.start()

    try:
        while running:
            state = con.receive()
            if state is None:
                print("No data received, robot might be disconnected or paused")
                break

            try:
                tcp_pose = state.actual_TCP_pose
                timestamp = state.timestamp
            except AttributeError:
                print("State did not contain actual_TCP_pose or timestamp; check configuration file")
                break

            latest_state["timestamp"] = timestamp
            latest_state["pose"] = tcp_pose

            print("TCP pose:", [round(v, 5) for v in tcp_pose])

            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nStopping capture...")
    finally:
        running = False
        try:
            con.send_pause()
        except Exception:
            pass
        con.disconnect()
        print("Disconnected")


if __name__ == "__main__":
    main()