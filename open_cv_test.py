import cv2 as cv
img = cv.imread("Grundriss Beispiele\Ziel\Beispiel_02.jpg")

gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

blurred = cv.GaussianBlur(gray, (5,5), 0)

edges = cv.Canny(blurred, 50, 150)

contours, _ = cv.findContours(edges, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
walls = cv.HoughLinesP(edges, 1, 1, 1)

for wall in walls:
    x1, y1, x2, y2 = wall[0]
    cv.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2) 



cv.imshow('Detected Rectangles', img) 
cv.waitKey(0) 
cv.destroyAllWindows() 