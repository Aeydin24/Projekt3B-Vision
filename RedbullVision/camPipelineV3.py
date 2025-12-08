import depthai as dai
import cv2
import time

class lorteFisseCameaPipeline:
    def __init__(self, pipeline, videoQueue, initFlag, vizFrame, cam, videoIn, vizualize):
        self.pipeline = pipeline
        self.videoQueue = videoQueue
        self.initFlag = initFlag
        self.vizFrame = vizFrame
        self.cam = cam
        self.videoIn = videoIn
        self.vizualize = vizualize

    def init_camera(self):
        if not self.initFlag and not self.pipeline.isRunning():
            print("pipeline already running")
            self.pipeline = dai.Pipeline()
            self.cam = self.pipeline.create(dai.node.Camera).build()
            self.videoQueue = self.cam.requestOutput((640, 480)).createOutputQueue()
            self.pipeline.start()
            time.sleep(2)
            self.initFlag = True
            print("pipeline started")
        else:
            print("pipeline already running")

    def close_camera(self):
        self.pipeline.stop()
        self.initFlag = False
        time.sleep(1)
        cv2.destroyAllWindows()
        print("pipeline stopped")

    def get_frame(self):
        if self.initFlag and self.pipeline.isRunning():
            videoIn = self.videoQueue.get()
            frame = videoIn.getCvFrame()
            return frame
        else:
            print("could not get frame")
            return None
        
    def display_frame(self):
        self.init_camera()
        while self.initFlag and self.pipeline.isRunning():

            normalFrame = self.get_frame()
            if normalFrame is not None and not self.vizualize:
                displayFrame = normalFrame

            elif self.vizFrame is not None and self.vizualize:
                displayFrame = self.vizFrame
            
            #PLEASE FUCNING DISLAY en frame for mmig
            cv2.imshow("shitty fucking lorte motherfucker indavelde FEED! viz or no viz bid i puden!", displayFrame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.close_camera()

if __name__ == "__main__":
    lorteFisseCameaPipeline.init_camera()

    