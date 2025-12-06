import depthai as dai
import cv2
import time

class CameraPipeline:
    def __init__(self, pipeline, videoQueue, initFlag, vizFrame, cam, videoIn, vizualize):
        self.pipeline = pipeline
        self.videoQueue = videoQueue
        self.initFlag = initFlag
        self.vizFrame = vizFrame
        self.cam = cam
        self.videoIn = videoIn
        self.vizualize = vizualize

shitCam = CameraPipeline(
    pipeline=None,
    videoQueue=None,
    initFlag=False,
    vizFrame=None,
    cam=None,
    videoIn=None,
    vizualize=False,
)

def init_camera():
    if not shitCam.initFlag:
        print("pipeline already running")
        shitCam.pipeline = dai.Pipeline()
        shitCam.cam = shitCam.pipeline.create(dai.node.Camera).build()
        shitCam.videoQueue = shitCam.cam.requestOutput((640, 480)).createOutputQueue()
        shitCam.pipeline.start()
        time.sleep(2)
        shitCam.initFlag = True
        print("pipeline started")
    else:
        print("pipeline already running")

def close_camera():
    shitCam.pipeline.stop()
    shitCam.initFlag = False
    time.sleep(1)
    cv2.destroyAllWindows()
    print("pipeline stopped")

def get_frame():
    if shitCam.initFlag and shitCam.pipeline.isRunning():
        shitCam.videoIn = shitCam.videoQueue.get()
        frame = shitCam.videoIn.getCvFrame()
        return frame
    else:
        print("could not get frame")
        return None
    
def display_frame():
    while shitCam.initFlag and shitCam.pipeline.isRunning():
        noramlFrame = get_frame()
        if noramlFrame is not None and not shitCam.vizualize:
            cv2.imshow("shitty fucking lorte motherfucker indavelde FEED!", noramlFrame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
        elif shitCam.vizualize is not None:
            cv2.imshow("shitty fucking lorte motherfucker indavelde FEED! nu med vizualize effekt", shitCam.vizFrame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
    close_camera()

if __name__ == "__main__":
    init_camera()

    