import cv2
import numpy as np
import win32gui
import os
from PIL import ImageGrab
from PIL import Image
from random import randrange
import pyautogui
import matplotlib.pyplot as plt
from matplotlib import image
import time

def mse(imageA, imageB):
	# the 'Mean Squared Error' between the two images is the
	# sum of the squared difference between the two images;
	# NOTE: the two images must have the same dimension
	err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
	err /= float(imageA.shape[0] * imageA.shape[1])
	
	# return the MSE, the lower the error, the more "similar"
	# the two images are
	return err
 
pil_grabbed_img = ImageGrab.grab([0,0,300,300])
pil_grabbed_img.save("test_image.png")

pil_imported_img = image.imread('test_image.png')
#print(pil_grabbed_img.mode)

# pil_image = np.array(pil_grabbed_img)
# print(pil_image)

pil_img= cv2.cvtColor(np.array(pil_grabbed_img), cv2.COLOR_RGB2BGR)
print(pil_img)

cv2_imported_img = cv2.imread('test_image.png')
# cv2.imshow('Imported Image',cv2_imported_img)
# cv2.waitKey(0)
# cv2.destroyAllWindows
# print(pil_grabbed_img)
# print('\n\n\n')
# print(pil_imported_img)
print('\n\n\n')
print(cv2_imported_img)

print(mse(pil_img,cv2_imported_img))

def PIL_ImageGrab_to_Opencv(image_in):
    image_out= cv2.cvtColor(np.array(image_in), cv2.COLOR_RGB2BGR)