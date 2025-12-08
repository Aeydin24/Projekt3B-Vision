import time
import cv2
import depthai as dai
import numpy as np
import products
from camPipelineV3 import lorteFisseCameaPipeline
from moveRobot import getCurrentPose

# load homography
data = np.load("homography.npz")
H = data["H"]

ROBOT_IP = "192.168.0.2"

def pixel_to_world(u: float, v: float):
    p = np.array([u, v, 1.0], dtype=np.float32)
    world = H @ p
    if abs(world[2]) < 1e-6:
        return None
    world /= world[2]
    return float(world[0]), float(world[1])

def get_all_products():
    # List of all product instances from products.py
    return [
        products.blue_box,
        products.green_box,
        products.red_pill_glass,
        products.green_pill_glass,
        products.black_pill_glass,
        products.yellow_pill_glass
    ]

def detect_objects(frame, product_list):
    candidates = []
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    for prod in product_list:
        # Create mask
        mask = cv2.inRange(hsv, prod.lower_color, prod.upper_color)
        
        # Clean up mask
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if prod.min_area < area < prod.max_area:
                # Check shape
                perimeter = cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, 0.04 * perimeter, True)
                
                shape_match = False
                if prod.shape == "box":
                    # Box should have approx 4 vertices
                    if len(approx) == 4:
                        shape_match = True
                elif prod.shape == "circle":
                    # Circle should have more vertices
                    if len(approx) > 4:
                        shape_match = True
                
                if shape_match:
                    M = cv2.moments(cnt)
                    if M["m00"] != 0:
                        cx = int(M["m10"] / M["m00"])
                        cy = int(M["m01"] / M["m00"])
                        
                        world_pos = pixel_to_world(cx, cy)
                        if world_pos:
                            candidates.append({
                                "product": prod,
                                "center": (cx, cy),
                                "world": world_pos,
                                "contour": cnt
                            })
    return candidates

def select_best_object(candidates, tcp_pose):
    if not candidates:
        return None
    # Sort by priority (lower is better)
    candidates.sort(key=lambda x: x["product"].priority)
    
    best_priority = candidates[0]["product"].priority
    top_candidates = [] 
    for c in candidates:
        if c["product"].priority == best_priority:
            top_candidates.append(c)     
    
    # If multiple with same priority, find closest to TCP
    tcp_x, tcp_y = tcp_pose[0], tcp_pose[1]
    best_candidate = None
    min_dist = float("inf")
    
    for cand in top_candidates:
        wx, wy = cand["world"]
        #euclidian formula beregner distance mellem to punkter
        dist = np.sqrt((wx - tcp_x)**2 + (wy - tcp_y)**2)
        if dist < min_dist:
            min_dist = dist
            best_candidate = cand
            
    return best_candidate

def get_target_pose(best_candidate, current_tcp_pose):
    if best_candidate is None:
        return None
    
    product = best_candidate["product"]
    x_w, y_w = best_candidate["world"]
    depot_location = product.depot_location
    
    # Start with current pose to keep rotation if not specified
    target_pose = list(current_tcp_pose)
    target_depot = list(current_tcp_pose)
    # Update position
    target_depot[0] = depot_location[0]
    target_depot[1] = depot_location[1]
    target_depot[2] = depot_location[2]
    target_pose[0] = x_w
    target_pose[1] = y_w
    target_pose[2] = product.z_pick
            
    return target_pose, target_depot

#note til mig selv over nej om rtde skal starte i en  funktion isteder for main
#note til mig selv overvej om vi skal starte cam pipeline i en funktion is istedet for.
def run_detection():

    product_list = get_all_products() #return en liste med alle produkter vi skal detektere
    start_time = time.time()
    sampleTime = 2 
    best_target_pose = None
    target_depot = None
    # Run detection for a limited time or until a good object is found
    while True:

        frame = lorteFisseCameaPipeline.get_frame()
        # ADD  en liste for  første frame som vi kan perspektivere til sidste frame. i while loopet. for at gøre sample time mere effektivt. (Farlig)
        # hvis postionere af objekter ikke har flytter sig cy og cx. inden for en margin der sat så kan vi køre efter sample time hvis ikke så reset timeren.
        if frame is None:
            print("Camera not initialized properly.")
            break

        # Get current TCP pose
        tcp_pose = getCurrentPose()
        candidates = detect_objects(frame, product_list)
        best_obj = select_best_object(candidates, tcp_pose)
        # Calculate target pose
        target_pose, depot_pose = get_target_pose(best_obj, tcp_pose)

        # Visualization
        if best_obj:
            cx, cy = best_obj["center"]
            prod_name = best_obj["product"].name
            cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)
            cv2.putText(frame, f"{prod_name}", (cx + 10, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(frame, f"({cx}, {cy})", (cx + 10, cy + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            lorteFisseCameaPipeline.vizFrame = frame
            
            if target_pose and time.time() - start_time < sampleTime:
                print(f"Target Pose found: {target_pose}")
                best_target_pose = target_pose
                target_depot = depot_pose
                # If we found a target, we can break early or keep looking for a better one
                # For now, let's return the first valid one we find
                break
                
    #cv2.destroyAllWindows()
    # Stop pipeline if needed, or let it be handled by context manager if we used one
    # Since init_camera starts it but doesn't return a context manager, we might need to stop it manually if we want to be clean
    # But for now, let's just return the result
    return best_target_pose, target_depot

if __name__ == "__main__":
    run_detection()

