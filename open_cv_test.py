import cv2 as cv
import numpy as np
import random 

#img = cv.imread("Grundriss Beispiele\Beispiel_David.png")
#img = cv.imread("Grundriss Beispiele\Grundriss_01_EG.jpg")
#img = cv.imread("Grundriss Beispiele\Ziel\Beispiel_01.png")
img = cv.imread("Grundriss Beispiele\Ziel\Beispiel_03.jpg")


gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

blurred = cv.GaussianBlur(gray, (7,7), 0)

edges = cv.Canny(blurred, 50, 150)

# Apply adaptive thresholding for binarization
binary = cv.adaptiveThreshold(
    blurred, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 2
)
cv.imshow("binary", binary)
# # Morphological operations
# kernel = np.ones((3, 3), np.uint8)
# cleaned = cv.morphologyEx(binary, cv.MORPH_CLOSE, kernel, iterations=1)

# # Optionally enhance contrast (histogram equalization)
# cleaned = cv.equalizeHist(cleaned)

# contours, _ = cv.findContours(cleaned, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)



#cv.drawContours(img, contours, -1, (0, 255, 0), 2)


# walls = cv.HoughLinesP(edges, rho=1, theta=np.pi/180, threshold=100, minLineLength=50, maxLineGap=10)

# for wall in walls:
#     x1, y1, x2, y2 = wall[0]
#     cv.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2) 

image_shape = img.shape
height, width = image_shape[0], image_shape[1]
b, g, r = 255, 255, 255  # orange
image = np.zeros((height, width, 3), np.uint8)
image[:, :, 0] = b
image[:, :, 1] = g
image[:, :, 2] = r

#cv.imshow("A New Image", image)


### This works in detecting most walls 
_, thresh = cv.threshold(gray, 150, 255, cv.THRESH_BINARY)
#cv.imshow('thresh', thresh) 

mor_img = cv.morphologyEx(thresh, cv.MORPH_OPEN, (5, 5), iterations=3)
#cv.imshow("mor_img", mor_img)
contours, _ = cv.findContours(mor_img, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

sorted_contours = sorted(contours, key=cv.contourArea, reverse=True)

for c in sorted_contours[1:]:
    area = cv.contourArea(c)
    if area > 1000:
        cv.drawContours(image, [c], -1, (random.randrange(0, 255), random.randrange(0, 256), random.randrange(0, 255)), 3)



### ChatGPT room detection

# # Step 2: Preprocess the image
# gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)  # Convert to grayscale
# _, binary = cv.threshold(gray, 200, 255, cv.THRESH_BINARY_INV)  # Thresholding to invert the image

# # Step 3: Detect contours
# contours, _ = cv.findContours(binary, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

# # Step 4: Filter and identify rectangular rooms
# rooms = []
# outer_boundary = None
# for contour in contours:
#     # Approximate the contour
#     epsilon = 0.02 * cv.arcLength(contour, True)
#     approx = cv.approxPolyDP(contour, epsilon, True)

#     # Check if it is a rectangle (4 vertices and is convex)
#     if len(approx) == 4 and cv.isContourConvex(approx):
#         # Further filter by area to remove small contours
#         area = cv.contourArea(approx)
#         if area > 100:  # Minimum area threshold to filter small noise
#             x, y, w, h = cv.boundingRect(approx)
#             aspect_ratio = float(w) / h

#             # Determine if it's the outer boundary or an internal room
#             if area > 100000:  # Large area likely represents the outer boundary
#                 outer_boundary = approx
#             else:
#                 rooms.append(approx)

# if outer_boundary is not None:
#     # Ensure outer_boundary is properly reshaped for pointPolygonTest
#     outer_boundary = outer_boundary.reshape(-1, 2)  # Convert to a 2D array of points
#     rooms = [
#         room for room in rooms
#         if len(room) > 0 and cv.pointPolygonTest(outer_boundary, tuple(room[0][0]), False) >= 0
#     ]
# # Step 5: Highlight detected rooms
# output_image = img.copy()
# for room in rooms:
#     cv.drawContours(output_image, [room], -1, (0, 255, 0), 3)  # Draw green rectangles

#  #Draw the outer boundary in a different color (optional)
# if outer_boundary is not None:
#     cv.drawContours(output_image, [outer_boundary], -1, (255, 0, 0), 3)  # Blue for outer boundary

# print(rooms)
# cv.imshow("Detected Rooms", output_image)

cv.imshow('img', image) 
cv.waitKey(0) 
cv.destroyAllWindows() 

cv.imwrite