import cv2 as cv
import numpy as np

img = cv.imread("Grundriss Beispiele\Beispiel_David.png")

gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

blurred = cv.GaussianBlur(gray, (7,7), 0)

edges = cv.Canny(blurred, 50, 150)

# Apply adaptive thresholding for binarization
binary = cv.adaptiveThreshold(
    blurred, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 2
)

# Morphological operations
kernel = np.ones((3, 3), np.uint8)
cleaned = cv.morphologyEx(binary, cv.MORPH_CLOSE, kernel, iterations=1)

# Optionally enhance contrast (histogram equalization)
cleaned = cv.equalizeHist(cleaned)

#contours, _ = cv.findContours(cleaned, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

#cv.drawContours(img, contours)
walls = cv.HoughLinesP(edges, rho=1, theta=np.pi/90, threshold=200, minLineLength=50, maxLineGap=20)

for wall in walls:
    x1, y1, x2, y2 = wall[0]
    cv.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2) 



cv.imshow('Detected Rectangles', img) 
cv.waitKey(0) 
cv.destroyAllWindows() 