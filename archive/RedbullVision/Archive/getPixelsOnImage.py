import cv2
import camPipelineV4 as camPipeline
import time
import depthai as dai   

mouse_x = 0
mouse_y = 0

def mouse_callback(event, x, y, flags, param):
    global mouse_x, mouse_y
    if event == cv2.EVENT_MOUSEMOVE:
        mouse_x = x
        mouse_y = y

def cameraFeed():
    pipeline = dai.Pipeline()
    cam = pipeline.create(dai.node.Camera).build()
    videoQueue = cam.requestOutput((640, 480)).createOutputQueue()
    pipeline.start()

    time.sleep(4)

    cv2.namedWindow('image')
    cv2.setMouseCallback('image', mouse_callback)

    while True:
        videoIn = videoQueue.get()
        frame = videoIn.getCvFrame()        
        if frame is None:
            break
        
        cv2.putText(frame, f"X: {mouse_x}, Y: {mouse_y}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow('image', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()


if __name__=="__main__":
    cameraFeed()