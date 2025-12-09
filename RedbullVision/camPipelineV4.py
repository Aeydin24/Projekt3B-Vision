import depthai as dai
import cv2
import time
from ultralytics import YOLO
import torch
from controlStates import sm, errorState
import rtde_control
ROBOT_IP = "192.168.0.2"
rtde_c = rtde_control.RTDEControlInterface(ROBOT_IP)

class camPipeline:
    pipeline = None
    videoQueue = None
    cam = None
    initFlag = False
    vizFrame = None
    vizualize = False 
    def init_camera():
        if not camPipeline.initFlag:
            print("setting up pipeline")
            camPipeline.pipeline = dai.Pipeline()
            camPipeline.cam = camPipeline.pipeline.create(dai.node.Camera).build()
            camPipeline.videoQueue = camPipeline.cam.requestOutput((640, 480)).createOutputQueue()
            camPipeline.pipeline.start()
            time.sleep(2)
            camPipeline.initFlag = True
            print("pipeline started")
        else:
            print("pipeline already running")

    def close_camera():
        camPipeline.pipeline.stop()
        camPipeline.initFlag = False
        time.sleep(1)
        cv2.destroyAllWindows()
        print("pipeline stopped")

    def get_frame():
        if camPipeline.initFlag and camPipeline.pipeline.isRunning():
            videoIn = camPipeline.videoQueue.get()
            frame = videoIn.getCvFrame()
            return frame
        else:
            print("could not get frame")
            return None
        

    def init_yolo():
        DEVICE = 0 if torch.cuda.is_available() else 'cpu'
        frame = camPipeline.get_frame()
        model = YOLO("yolo11n.pt")
        yoloFrame = model(frame, device=DEVICE, verbose=False, classes=[0], conf=0.8)
        person_detected = False
        for r in yoloFrame:
            if len(r.boxes) > 0:   # YOLO detected something
                person_detected = True
                print("Person detected!")
        if person_detected:
            rtde_c.triggerProtectiveStop()
            sm.changeState(errorState())
                
        
    def display_frame():
        camPipeline.init_camera()
        while camPipeline.initFlag and camPipeline.pipeline.isRunning():
            camPipeline.init_yolo()
            normalFrame = camPipeline.get_frame()
            if normalFrame is not None and not camPipeline.vizualize:
                displayFrame = normalFrame

            elif camPipeline.vizFrame is not None and camPipeline.vizualize:
                displayFrame = camPipeline.vizFrame

            #PLEASE FUCNING DISLAY en frame for mmig
            cv2.imshow("shitty fucking lorte motherfucker indavelde FEED! viz or no viz bid i puden!", displayFrame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        camPipeline.close_camera()




    