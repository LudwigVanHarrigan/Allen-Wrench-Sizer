
import imutils
import cv2

#To do:
# - Organize this mess. Could we use an object oriented structure?
# - Implement some system to convert area ranges to allen wrench values
# - Turn off continuous streaming? We only need a picture when we're scanning a wrench
# - Lock camera settings (zoom, exposure, focus, etc.) somehow

cam = cv2.VideoCapture(0)

cam.set(3, 1920)  # Set horizontal resolution
cam.set(4, 1080)  # Set vertical resolution


while(True):
	ret, frame = cam.read() #Not sure what the first returned thingy is
	
	
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	blurred = cv2.GaussianBlur(gray, (5, 5), 0)
	thresh = cv2.threshold(blurred, 80,255,cv2.THRESH_BINARY)[1] #Simple binary threshold; anything over 60 gets turned to 255, anything under 60 gets turned to 0
	thresh = cv2.bitwise_not(thresh) #invert the image (black to white, since black is 0 and findContours looks for anything BUT 0)
	contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #Finds contours in the image. The 2nd and 3rd arguments are  the retrieval mode and contour simplification mode respectively. I'm not sure why it requires a .copy() of the image... maybe it tries to change it? 
	contours = imutils.grab_contours(contours) #parse the output of findContours with Adrian (from PyImageSearch)'s fancy imutils library

# Get a list of the areas of all the contours (in preparation of picking the biggest one)
	contour_areas = []
	for contour in contours: 
		contour_areas.append(cv2.contourArea(contour)) #calculates the area of the contour

	
	
	if(len(contour_areas) > 0): #If there are any contours, 
		contour_areas.sort() #Sort all the contour areas from largest to smallest
		wrench_area = contour_areas[(len(contour_areas)-1)] #get the last item (the largest) in the list. Note that len() returns the size (say, 5 elements) but the last element has index len()-1 (which would be 4)
		print(wrench_area)
		cv2.drawContours(image=frame, contours=contours, contourIdx=-1, color=(0,255,0), thickness=1)
		
	
	
	#print(type(thresh))
	cv2.imshow('Video output',frame)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break
 
cam.release()
cv2.destroyAllWindows()



