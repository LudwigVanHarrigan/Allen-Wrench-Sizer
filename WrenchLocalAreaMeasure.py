from time import sleep
import imutils
import cv2
import numpy as np
from scipy import stats
from math import atan, atan2, degrees, sin, cos, pi
import subprocess

#To do:
# - Organize this mess. Could we use an object oriented structure?
# - Implement some system to convert area ranges to allen wrench values
# - Turn off continuous streaming? We only need a picture when we're scanning a wrench
# - Lock camera settings (zoom, exposure, focus, etc.) somehow


def findSlope (point1, point2):
	#Do stuff!
	#Point1 should be contour[n], and Point2 is contour[n+1]
	#This will likely cause index errors to work through. Yay!
	#A point should be [x, y] because that makes sense; It's probably something different though
	run = point2[0]-point1[0] #point[0] is the distance across from the top left corner, aka X
	rise = point2[1]-point1[1] #Point[1] is the distance DOWN from the top left corner, aka -Y, but I'll call it Y for now.
	#Downward slopes will be positive.
	
	rise = float(rise) #Because I don't know how smart Python is
	run = float(run) 
	if(not run == 0):
		slope = rise/run
	else:
		slope = float('inf') #Python's Infinity!
	
	#---DEBUG STUFF---
	#print("Rise: " + str(rise))
	#print("Run: " + str(run))
	#---END DEBUG---             (I feel like a pro)
	
	return slope 
	
	
	

	
def contourToSlopes (contour, pointSkip=4):
	
	subDivisions = int(np.ceil(len(contour)/pointSkip)) #If we count by pointSkip, we count this many items. The ceil is to make it a nice number that we can use it in a for loop. Note that since we're always rounding up, and we're multiplying by the same number we just divided by (later), we won't do a indexOutOfBounds.
	slopes = [] ; # All the slopes in one place
	for i in range(subDivisions): 
		subi = i*pointSkip #subdivided i; the index we'll be asking for
		if i == subDivisions-1: #If we're on the last one, check against the first point.
			point1 = contour[subi][0]
			point2 = contour[0][0]
		else: # Otherwise, check against the next point
			point1 = contour[subi][0]
			point2 = contour[subi+pointSkip][0] #Remember, subi = i*pointSkip, so subi+pointSkip = (i+1)*pointSkip.
		slopes.append(findSlope(point1, point2))
	return slopes
	
def generateLineContour (point1, point2): #Makes a contour that can be added to contours to be drawn
	#Each point should take the form [x, y]
	point1 = np.asarray(point1) #Because I don't know how smart the user is, we'll convert array_like to np array
	point2 = np.asarray(point2)
	return np.array([[point1],[point2]]) #Note the extra set of brackets around each point!!
	

def generateLineImage(point1=(0,0), point2=(500,500), size=300):
	
	return cv2.line(np.zeros((v_res, h_res,1), dtype = "uint8"), point1, point2, color=255, thickness=size)
	
	
def findBoxCenter(box_points):
	#the output of minAreaRect() looks like [point, point, point, point]
	#where point is a [x, y]
	#I'm just going to do the midpoint of the diagonal
	x1 = box_points[0][0]
	y1 = box_points[0][1]
	x2 = box_points[2][0]
	y2 = box_points[2][1]
	
	midx = int(np.round((x1+x2)/2))
	midy = int(np.round((y1+y2)/2))
	return (midx, midy)
	
def generateMeasureyLine(point, angle, length=300):
	#Point should be an [x,y] or (x,y), and angle should be from -pi/2 to pi/2 in radians.
	#That is, a reference angle.
	x_del = (length/2)*cos(angle)
	y_del = (length/2)*sin(angle)


	
	x1 = point[0] + x_del
	x2 = point[0] - x_del
	y1 = point[1] + y_del
	y2 = point[1] - y_del
	
	return (int(np.round(x1)), int(np.round(y1))), (int(np.round(x2)), int(np.round(y2))) #point, point. Can be fed right into generateLineImage or generateLineContour, I hope.

def pxToMM(px):

	return (0.124*px) + 0.468




###-----Wrench Measuring Constants and Variables-----###

MEASURE_WIDTH = 300

WRENCH_SIZES = {6.34: '0.050',
				9.00: '1/16',
				12.25: '5/64',
				15.53: '3/32',
				18.95: '7/64'}



cam_props = {'brightness': 128, 'contrast': 128, 'saturation': 180,
             'gain': 0, 'sharpness': 125, 'exposure_auto': 0,
             'exposure_absolute': 9, 'exposure_auto_priority': 0,
             'focus_auto': 0, 'focus_absolute': 200, 'zoom_absolute': 100,
             'white_balance_temperature_auto': 0, 'white_balance_temperature': 5200}

#for key in cam_props:
#	subprocess.call(['v4l2-ctl -d /dev/video2 -c {}={}'.format(key, str(cam_props[key]))], shell=True) # Set camera settings

cam = cv2.VideoCapture(0 + cv2.CAP_V4L2)

cam_h_res = 1920  
cam_v_res = 1080 #Set resolution. This used to be called v_res.
h_crop = 1500
v_crop = 1080
h_res = h_crop if (h_crop < cam_h_res) else cam_h_res #The actual final resolution
v_res = v_crop if (v_crop < cam_v_res) else cam_v_res

#Where's the middle?
cam_h_half = int(cam_h_res/2)
cam_v_half = int(cam_v_res/2)
h_half_crop = min(int(h_crop/2), cam_h_half)
v_half_crop = min(int(v_crop/2), cam_v_half) #The min check is because we'll never have a crop bigger than the source frame
center_x = h_half_crop if (h_crop < cam_h_res) else cam_h_half #the actual final center. May be redundant.
center_y = v_half_crop if (v_crop < cam_v_res) else cam_v_half

cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')) #Set to stream mjpeg; otherwise we don't get full framerate
cam.set(3, cam_h_res)  # Set horizontal resolution
cam.set(4, cam_v_res)  # Set vertical resolution
# Other settings. Possible settings can be found with v4l2-ctl -d /dev/videoX -l
#cam.set(cv2.CAP_PROP_FOCUS, 220) # Set focus. Each 100 here is 25 in v4l2-ctrl -c speak
#cam.set(cv2.CAP_PROP_EXPOSURE, 9) # Manual exposure
#cam.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1) # Turn off auto mode
#cam.set(cv2.CAP_PROP_WB_TEMPERATURE, 5200) # White Balance
#cam.set(cv2.CAP_PROP_FPS, 30)  # Set Framerate
sleep(1.0)
for key in cam_props:
	subprocess.call(['v4l2-ctl -d /dev/video0 -c {}={}'.format(key, str(cam_props[key]))], shell=True)


while(True):
	ret, frame = cam.read() #Not sure what the first returned thingy is
	
	if (v_crop < cam_v_res) or (h_crop < cam_h_res): #Only krop if we need to!
		frame = frame[cam_v_half-v_half_crop : cam_v_half+v_half_crop, cam_h_half-h_half_crop : cam_h_half+h_half_crop] #Krop!
		
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	blurred = cv2.GaussianBlur(gray, (5, 5), 0)
	thresh = cv2.threshold(blurred, 60,255,cv2.THRESH_BINARY)[1] #Simple binary threshold; anything over 60 gets turned to 255, anything under 60 gets turned to 0
	thresh = cv2.bitwise_not(thresh) #invert the image (black to white, since black is 0 and findContours looks for anything BUT 0)
	
	#Finds contours in the image. The 2nd and 3rd arguments are  the retrieval mode and contour simplification mode respectively. 
	contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE) 
	#I'm not sure why it requires a .copy() of the image... maybe it tries to change it? 
	contours = imutils.grab_contours(contours) #parse the output of findContours with Adrian (from PyImageSearch)'s fancy imutils library

# Get a list of the areas of all the contours (in preparation of picking the biggest one)
	
	largest_contour_index = 0 #declare this stuff globally!
	largest_contour = 0
	for i, contour in enumerate(contours): #enumerate(things) returns (i, thing) where i is the index of thing in things. 
	#This lets us remember exactly WHERE the biggest contour is, not just WHAT it is.
		contour_area = cv2.contourArea(contour) #How big is the contour?
		if  contour_area > largest_contour: #If we have a new champion...
			largest_contour = contour_area # give it the belt
			largest_contour_index = i # ...and get its address (for the paparazzi)
	# Then keep looping until the absolute best champion has been found
	# Note that now, largest_contour will still get us the largest contour's area
	# We can also get it with cv2.contourArea(contours[largest_contour_index])




	if(len(contours) > 0): #If there are any contours, we can do contour stuff
	
		#contours[contour][point][point holder (zero)][coordinate]
		#contours is weird. The x coordinate is in a point is in a point holder is in a contour is in Contours. 
		#The point holder is the second [0], and 'point holder' is just my name for it.
		#I bet it can hold something else...
		contour = contours[largest_contour_index] 
		slopeys = contourToSlopes(contour, pointSkip=10) 
		mode, count = stats.mode(slopeys)
		slopesMode = float(mode[0]) #Because I don't know how smart stats.mode() is
		#print("Mode Slope: " + str(slopesMode))
		
		
		box = cv2.minAreaRect(contours[largest_contour_index])
		box_points = np.int0(cv2.boxPoints(box))
		
		#drawn_contour = [box_points] #Since drawContours() expects an array of contours (arrays of points) and boxPoints() returns an array of points, we must put it in another layer of list. Note that if we want to add anything else to be drawn, we can simply append it to drawn_contour.
		drawn_contour = contours
		drawn_contour.append(box_points)
		
		'''
		x2 = center_x + 100
		y2 = center_y + int(np.round(100*slopesMode))
		slopeLine = generateLineContour([center_x, center_y], [x2, y2])
	
		#print(slopeLine)
		drawn_contour.append(slopeLine)
		'''
		#print(degrees(atan(slopesMode))) # Degrees of the allen wrench. Note that positive angles are pointing down.

		box_center = findBoxCenter(box_points)
		measureP1, measureP2 = generateMeasureyLine(box_center, atan(slopesMode)+(pi/2), length=100) 
		
		lineImage = generateLineImage(measureP1, measureP2, size = MEASURE_WIDTH) #Make the measuring stick image
		measureImage = cv2.bitwise_and(thresh, lineImage) # AND it with the monochrome threshold image
		print(np.count_nonzero(measureImage)/MEASURE_WIDTH) # Count the number of white pixels
		print(degrees(atan(slopesMode)))
		cv2.drawContours(image=frame, contours=drawn_contour, contourIdx=-1, color=(0,255,0), thickness=1)


	#print(type(thresh))
	cv2.imshow('Video output',frame) 
	#cv2.imshow('Measuring Stick', measureImage)
	if cv2.waitKey(1) & 0xFF == ord('q'): #If you press q
		break

cam.release()
cv2.destroyAllWindows()


