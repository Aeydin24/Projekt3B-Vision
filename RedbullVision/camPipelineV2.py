import depthai as dai
import cv2
import time

class CameraPipeline:
    def __init__(self, pipeline, videoQueue, init_flag, frame, cam):
        self.pipeline = pipeline
        self.videoQueue = videoQueue
        self.init_flag = init_flag
        self.frame = frame
        self.cam = cam

shitCam = CameraPipeline(
    pipeline=None,
    videoQueue=None,
    init_flag=False,
    frame=None
    cam=None
)


def init_camera():
    if not shitCam.init_flag:
        print("pipeline already running")
        shitCam.pipeline = dai.Pipeline()
        shitCam.cam = shitCam.pipeline.create(dai.node.Camera).build()
        shitCam.videoQueue = shitCam.cam.requestOutput((640, 480)).createOutputQueue()
        shitCam.pipeline.start()
        time.sleep(2)
        shitCam.init_flag = True
        print("pipeline started")
    else:
        print("pipeline already running")



def close_camera():
    shitCam.pipeline.stop()
    time.sleep(1)
    shitCam.init_flag = False
    print("pipeline stopped")


def init_camera(flag):
    print("before doing pipeline .dai")
    if flag == False:
        global pipeline
        pipelineGet = dai.Pipeline()
        pipeline = pipelineGet

    if not pipeline.isRunning():
        print("this is the start of the if statement")        
        cam = pipeline.create(dai.node.Camera).build()
        global videoQueue
        videoQueueGet = cam.requestOutput((640, 480)).createOutputQueue()
        videoQueue = videoQueueGet
        pipeline.start()
        time.sleep(2)
        print("pipeline started")
    else:
        print("this is before videoQueue in else")
        videoQueue = videoQueue
        print("pipeline already running")
    return pipeline, videoQueue

def image_capture():
    pipeline, videoQueue = init_camera(flag=False)
    while pipeline.isRunning():
        videoIn = videoQueue.get()
        frame = videoIn.getCvFrame()
        if frame is not None:
            cv2.imshow("Camera Frame", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
    pipeline.stop()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    # Start it asynchronously:
    image_capture()

    