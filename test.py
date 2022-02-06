

import cv2
import numpy as np

 

img = cv2.imread('test.jpg')

print(img.shape) # Print image shape
cv2.imshow("original", img)
