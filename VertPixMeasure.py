
import imutils
import cv2
import numpy as np


# Set vertical and horizontal resolution. For some reason the Logi c930e can go up to 1296x2304...
VertResolution = 1080
HorizResolution = 1920


img_center = int(HorizResolution/2)
#To do:
# - Organize this mess. Could we use an object oriented structure?
# - Implement some system to convert area ranges to allen wrench values
# - Turn off continuous streaming? We only need a picture when we're scanning a wrench
# - Lock camera settings (zoom, exposure, focus, etc.) somehow

cam = cv2.VideoCapture(0)

cam.set(3, HorizResolution)  # Set horizontal resolution
cam.set(4, VertResolution)  # Set vertical resolution



while(True):
	ret, frame = cam.read() #Not sure what the first returned thingy is
	
	
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	blurred = cv2.GaussianBlur(gray, (5, 5), 0)
	thresh = cv2.threshold(blurred, 80,255,cv2.THRESH_BINARY)[1] #Simple binary threshold; anything over 80 gets turned to 255, anything under 60 gets turned to 0
	thresh = cv2.bitwise_not(thresh) #invert the image (black to white, since black is 0 and we generally look for anything BUT 0)
	
	cnt = np.count_nonzero(thresh[:, img_center]) #Count the number of non-black (i.e. white) pixels in the column of the image that is in the center. 
	#The above is a cheap test thingy to see if I can accurately detect the width of an allen wrench, without writing code to detect the allen wrench and actually measure across it.
	print(cnt)
	

	
	#Start drawing stuff. This should be done AFTER calculations.
	#print(type(thresh))
	display = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR) #You can't draw color on a gray image
	display = cv2.line(img=display, pt1=(img_center, 0), pt2=(img_center, VertResolution), color=(0,255,0), thickness=1) #show where the measurement point is
	
	cv2.imshow('Video output', display)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break
 
cam.release()
cv2.destroyAllWindows()



