import cv2
import numpy as np

objp = np.zeros((6 * 9, 3), np.float32)
objp[:, :2] = np.mgrid[0:9, 0:6].T.reshape(-1, 2)

img = cv2.imread("homographyImage.png")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

ret, corners = cv2.findChessboardCorners(gray, (9, 6), None)

if ret:
    print("Found chessboard corners:")
    print(corners)
    print("Number of corners:", len(corners))

    # Refine corner locations (optional but improves accuracy)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)

    # Draw and display the corners
    cv2.drawChessboardCorners(img, (9, 6), corners2, ret)
    cv2.imshow("Detected Chessboard Corners", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    print("Chessboard corners not found.")