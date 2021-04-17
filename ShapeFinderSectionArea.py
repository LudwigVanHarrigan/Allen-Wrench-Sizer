from time import sleep
import imutils
import cv2
import numpy as np

#To do:
# - Organize this mess. Could we use an object oriented structure?
# - Implement some system to convert area ranges to allen wrench values
# - Turn off continuous streaming? We only need a picture when we're scanning a wrench
# - Lock camera settings (zoom, exposure, focus, etc.) somehow

cam = cv2.VideoCapture(0)
v_res = 480
h_res = 640
v_crop = 720
h_crop = 1000


v_half = int(v_res/2)
h_half = int(h_res/2)
v_half_crop = int(v_crop/2)
h_half_crop = int(h_crop/2)


cam.set(3, h_res)  # Set horizontal resolution
cam.set(4, v_res)  # Set vertical resolution
sleep(2.0)



while(True):
	ret, frame = cam.read() #Not sure what the first returned thingy is
	
	if (v_crop < v_res) or (h_crop < h_res): #Only krop if we need to!
		frame = frame[v_half-v_half_crop : v_half+v_half_crop, h_half-h_half_crop : h_half+h_half_crop]
	
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	blurred = cv2.GaussianBlur(gray, (5, 5), 0)
	thresh = cv2.threshold(blurred, 80,255,cv2.THRESH_BINARY)[1] #Simple binary threshold; anything over 60 gets turned to 255, anything under 60 gets turned to 0
	thresh = cv2.bitwise_not(thresh) #invert the image (black to white, since black is 0 and findContours looks for anything BUT 0)
	contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #Finds contours in the image. The 2nd and 3rd arguments are  the retrieval mode and contour simplification mode respectively. I'm not sure why it requires a .copy() of the image... maybe it tries to change it? 
	contours = imutils.grab_contours(contours) #parse the output of findContours with Adrian (from PyImageSearch)'s fancy imutils library

# Get a list of the areas of all the contours (in preparation of picking the biggest one)
	
	largest_contour_index = 0
	largest_contour = 0
	for i, contour in enumerate(contours): #enumerate returns (i, thing) where i is the index of thing in things. This lets us remember exactly WHERE the biggest contour is, not just WHAT it is.
		contour_area = cv2.contourArea(contour) #How big is the contour?
		if  contour_area > largest_contour: #If we have a new champion...
			largest_contour = contour_area # give it the belt
			largest_contour_index = i # ...and get its address (for the paparazzi)
	# Then keep looping until the absolute best champion has been found
	# Note that now, largest_contour will get us the largest contour, but we can also get it with cv2.contourArea(contours[largest_contour_index])




	if(len(contours) > 0): #If there are any contours, we can do contour stuff
	#if(True):	
		#print(largest_contour)
		box = cv2.minAreaRect(contours[largest_contour_index])
		box_points = np.int0(cv2.boxPoints(box))
		
		drawn_contour = [box_points] #Since drawContours() expects an array of arrays of points and boxPoints() returns an array of points, we must put it in another layer of list. Note that if we want to add anything else to be drawn, we can simply append it to drawn_contour.
		cv2.drawContours(image=frame, contours=drawn_contour, contourIdx=-1, color=(0,255,0), thickness=1)
		
		
	#print(type(thresh))
	cv2.imshow('Video output',frame)
	if cv2.waitKey(1) & 0xFF == ord('q'): #If you press q
		break
 
cam.release()
cv2.destroyAllWindows()


