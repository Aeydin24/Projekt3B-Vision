import StateMachine
import cv2
import depthai as dai
import numpy as np 


#-----------------------------

def getVideo():

    with dai.Pipeline() as pipeline:
            cam = pipeline.create(dai.node.Camera).build()
            videoQueue = cam.requestOutput((640, 480)).createOutputQueue()

            pipeline.start()
            print("Camera started. Press 'g' to move to red object, 'q' to quit.")

            while pipeline.isRunning():
                videoIn = videoQueue.get()
                frame = videoIn.getCvFrame()    
            
            return frame





# ---------- Show frame ----------

grayVideo = cv2.cvtColor(getVideo(), cv2.COLOR_BGR2GRAY)
        
#-----------functions--------------


    #---------- CIRCLE DETECTION ----------
def detect_circles(self, frame_gray):
    blur = cv2.medianBlur(frame_gray, (3), 2)
    circles = cv2.HoughCircles(

        blur, cv2.HOUGH_GRADIENT, 
        dp=1, 
        minDist=100,
        minRadius=90,
        maxRadius=100,
        param1=10
        param2=40
        )
    return circles
   
#---------- SQUARE-----------------

def detect_squares(self, frame_gray):
    blur = cv2.GaussianBlur(frame_gray, (5,5), 2) #??
    edges = cv2.Canny(blur,50,150,apertureSize = 3) # ???
    countours, _= cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)# find contours ???
    squares = []

    for cnt in countours:
        epsilon = 0.05 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)

        # check polygon with 4 corners
        if len(approx) == 4:
            # område skal være større end lidt støj
            area = cv2.contourArea(approx)
            if area > 200:  
                squares.append(approx)

        return squares
    

square = detect_squares(grayVideo)
    
    
#---------- COLOR DETECTION ----------
def detectColors(self, frame_bgr,  x, y, r):
    x1, y1 = max(0, x - r), max(0, y - r)
    x2, y2 = min(x + r, frame_bgr.shape[1]), min(y + r, frame_bgr.shape[0])

    roi = frame_bgr[y1:y2, x1:x2]
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    # ranges for colors
    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])

    lower_green = np.array([40, 40, 40])
    upper_green = np.array([80, 255, 255])

    lower_yellow = np.array([25, 100, 100])
    upper_yellow = np.array([35, 255, 255])
        # masks
    mask_red = cv2.inRange(hsv, lower_red1, upper_red1) | cv2.inRange(hsv, lower_red2, upper_red2)
    mask_green = cv2.inRange(hsv, lower_green, upper_green)
    mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)

    counts = {
    "red": cv2.countNonZero(mask_red),
    "green": cv2.countNonZero(mask_green),
    "yellow": cv2.countNonZero(mask_yellow),
    } 
    return max(counts, key=counts.get)  





if square:
    for sq in square:
        cv2.polylines(getVideo(), [sq], True, (255,0,0), 2)

        # Find center
        M = sq.reshape(4,2)
        cx = int(np.mean(M[:,0]))
        cy = int(np.mean(M[:,1]))
        r = 20  # lille ROI

        dominant = detectColors(getVideo(), cx, cy, r)

        objectList = {
            "shape": "square",
            "x": cx,
            "y": cy,
            "color": dominant
        }
        objectList.append(objectList)
    #----------- draw rectangle ---------
    cv2.polylines(getVideo(), [sq], True, (255,0,0), 2)   
    # -----------Find color square------- 
    dominant = detectColors(getVideo(), x, y, r)
    # -----------write color -----------
    cv2.putText(getVideo(), dominant, (x - w, y - h - 10),(0,255,255),2)
    
    objectList = {
        "shape": "square",
        "x": x, 
        "y": y, 
        "w": w,
        "h": h,
        "color": dominant
    }
    

#---------- Find circles ------------
circles = detect_circles(grayVideo)
            

if circles is not None:
    circles = np.uint16(np.around(circles))

    for c in circles[0, :]:
        x, y, r,  = c[0], c[1], c[2],
        x =int(x)
        y =int(y)
        w =int(r)
                

        # tegner cirkel
        cv2.circle(getVideo(), (x, y), r, (0, 255, 0), 2)

# ---- Find farve ----
dominant = detectColors(getVideo(), x, y, r)

# skriv farve på skærmen
cv2.putText(getVideo(), dominant, (x - r, y - r - 10),
    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

objectdict = {
    "shape": "circle",
    "x": x, 
    "y": y, 
    "r": r,
    "color": dominant
    }

self.ctrl.objectList.append(objectdict)
                                        
                


cv2.imshow("Analyze Feed", getVideo())
cv2.imshow("grayVideo Feed", grayVideo)

if cv2.waitKey(1) == ord('q'):
    cv2.destroyAllWindows()

    self.ctrl.machine.ChangeState(MovingState(self.ctrl))


    # ---------- DETECTION HELPERS ----------





