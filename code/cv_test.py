import cv2 as cv 
import numpy as np

img = cv.imread("Neue Grundrisse/D-Str/D-str._Obergeschoss_v3_cropped.jpg")
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
blurred = cv.GaussianBlur(gray, (7,7), 0)
edges = cv.Canny(blurred, 50, 150)

# Apply adaptive thresholding for binarization
# binary = cv.adaptiveThreshold(
#     blurred, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 2
# )

_, binary = cv.threshold(img,127,255,cv.THRESH_BINARY_INV)


contours, _ = cv.findContours(edges, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

#Morphological operations
kernel = np.ones((3, 3), np.uint8)
cleaned = cv.morphologyEx(binary, cv.MORPH_CLOSE, kernel, iterations=1)
#cleaned = cv.equalizeHist(cleaned)
cv.imshow("binary", cleaned)
#cv.imshow("bry", binary)

cv.waitKey(0) 
cv.destroyAllWindows() 