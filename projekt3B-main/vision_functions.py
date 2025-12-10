import numpy as np
import depthai as dai
import time
import cv2

class VisionSystem:
    def __init__(self):
        self.best_candidate = None
        self.best_priority = None
        self.pipeline = None
        self.videoQueue = None
        self.cam = None
        self.initFlag = False
        self.candidates = None
        self.top_candidates = None
        self.target_pose = None
        self.target_depot = None

    def init_camera(self):
        if not self.initFlag:
            print("setting up pipeline")
            self.pipeline = dai.Pipeline()
            self.cam = self.pipeline.create(dai.node.Camera).build()
            self.videoQueue = self.cam.requestOutput((640, 480)).createOutputQueue()
            self.pipeline.start()
            time.sleep(10)
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
        displayFrame = None
        while self.initFlag and self.pipeline.isRunning():
            normalFrame = self.get_frame()
            cv2.imshow("display_frame feed", normalFrame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        self.close_camera()

    def pixel_to_world(self, u: float, v: float, H):
        p = np.array([u, v, 1.0], dtype=np.float32)
        world = H @ p
        if abs(world[2]) < 1e-6:
            return None
        world /= world[2]
        return float(world[0]), float(world[1])

    def getHomography(self):
        try:
            data = np.load("homography.npz")
            H = data["H"]
        except FileNotFoundError:
            print("Theres no file called homography.npz")
            return None
        return H

    def detect_objects(self, frame, product_list, homografi):
        self.candidates = []
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        for prod in product_list:
            # Create mask
            mask = cv2.inRange(hsv, prod.lower_color, prod.upper_color)
            # Clean up mask
            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            #  husk kims gaussian blur
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if prod.min_area < area < prod.max_area:
                    # Check shape
                    perimeter = cv2.arcLength(cnt, True)
                    approx = cv2.approxPolyDP(cnt, 0.025 * perimeter, True)
                    shape_match = False
                    if prod.shape == "box":
                        # Box should have approx 4 vertices
                        if len(approx) == 4:
                            shape_match = True
                        else:
                            print("no len match for shape: box")
                    elif prod.shape == "circle":
                        # Circle should have more vertices
                        if len(approx) > 4:
                            shape_match = True
                        else:
                            print("no len match for shape: circle")
                    if shape_match:
                        M = cv2.moments(cnt)
                        if M["m00"] != 0:
                            cx = int(M["m10"] / M["m00"])
                            cy = int(M["m01"] / M["m00"])
                            worldPos = self.pixel_to_world(cx, cy, homografi)
                            if worldPos:
                                self.candidates.append({
                                    "product": prod,
                                    "center": (cx, cy),
                                    "world": worldPos,
                                    "contour": cnt
                                })
                            else:
                                print("No candidates were found.")
        return self.candidates

    def select_best_object_v2(self):
        if not self.candidates:
            return None
        # Sort by priority (lower = better)
        self.candidates.sort(key=lambda x: x["product"].priority)
        self.best_candidate = None
        # The first in the sorted list is the best candidate
        self.best_candidate = self.candidates[0]
        # Save the priority for reference
        self.best_priority = self.best_candidate["product"].priority
        return self.best_candidate

    def select_best_object_deprecated(self, tcp_pose):
        if not self.candidates:
            return None
        # Sort by priority (lower is better)
        self.candidates.sort(key=lambda x: x["product"].priority)
        self.best_priority = self.candidates[0]["product"].priority
        self.top_candidates = []
        for c in self.candidates:
            if c["product"].priority == self.best_priority:
                self.top_candidates.append(c)
                # If multiple with same priority, find closest to TCP
        tcp_x, tcp_y = tcp_pose[0], tcp_pose[1]
        self.best_candidate = None
        min_dist = float("inf")
        for cand in self.top_candidates:
            wx, wy = cand["world"]
            # euclidian formula beregner distance mellem to punkter
            dist = np.sqrt((wx - tcp_x) ** 2 + (wy - tcp_y) ** 2)
            if dist < min_dist:
                min_dist = dist
                self.best_candidate = cand
        return self.best_candidate

    def get_target_pose(self, tcp_pose):
        if self.best_candidate is None:
            return None, None
        product = self.best_candidate["product"]
        x_w, y_w = self.best_candidate["world"]
        depot_location = product.depot_location
        # Start with current pose to keep rotation if not specified
        self.target_pose = list(tcp_pose)
        self.target_depot = list(tcp_pose)
        # Update position
        self.target_depot[0] = depot_location[0]
        self.target_depot[1] = depot_location[1]
        self.target_depot[2] = depot_location[2]
        self.target_pose[0] = x_w
        self.target_pose[1] = y_w
        self.target_pose[2] = product.z_pick
        return self.target_pose, self.target_depot

    def get_all_products(self):
        # List of all product instances from products.py
        return [
            green_pill_glass,
            blue_pill_glass,
            pink_pill_glass,
            yellow_pill_glass
        ]

class productType:
    def __init__(self, name, shape, priority, lower_color, upper_color, min_area, max_area, z_pick, depot_location):
        self.name = name
        self.shape = shape
        self.priority = priority # lavere nummer = højere prioritet
        # HSV-farver som numpy-arrays
        self.lower_color = np.array(lower_color, dtype=np.uint8)
        self.upper_color = np.array(upper_color, dtype=np.uint8)
        self.min_area = min_area
        self.max_area = max_area
        # z-højde hvor vi vil samle objektet op (i meter)
        self.z_pick = z_pick
        self.depot_location = depot_location

pink_pill_glass = productType(
    name="pink_pill_glass",
    shape="circle",
    priority=4,
    lower_color=[145, 120, 120],
    upper_color=[165, 255, 255],
    min_area=300,
    max_area=50000,
    z_pick=0.06,
    depot_location= [-0.21798, 0.001067, 0.2]
)

green_pill_glass = productType(
    name="green_pill_glass",
    shape="circle",
    priority=1,
    lower_color=[38, 99, 78],
    upper_color=[58, 219, 198],
    min_area=300,
    max_area=50000,
    z_pick=0.06,
    depot_location=[-0.28627, 0.00845, 0.185]
)

yellow_pill_glass = productType(
    name="yellow_pill_glass",
    shape="circle",
    priority=2,
    lower_color=[14, 191, 151],
    upper_color=[34, 255, 255],
    min_area=300,
    max_area=50000,
    z_pick=0.06,
    depot_location=[-0.34390, -0.00825, 0.185]
)

blue_pill_glass = productType(
    name="blue_pill_glass",
    shape="circle",
    priority=3,
    lower_color=[92, 172, 93],
    upper_color=[112, 255, 213],
    min_area=300,
    max_area=50000,
    z_pick=0.06,
    depot_location=[-0.21798, 0.001067, 0.185]
)