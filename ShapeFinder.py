import argparse
import imutils
import cv2


#argparser = argparse.ArgumentParser()
#argparser.add_argument ("-i", "--image", #required=True, help="path to the image")
#args = vars(argparser.parse_args())
#image = cv2.imread(args["image"])

image = cv2.imread("AllenWrench3mm2.png") # A test image

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
thresh = cv2.threshold(blurred, 40,255,cv2.THRESH_BINARY)[1] #Simple binary threshold; anything over 60 gets turned to 255, anything under 60 gets turned to 0

thresh = cv2.bitwise_not(thresh) #invert the image (black to white, since black is 0 and findContours looks for anything BUT 0)

contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #Finds contours in the image. The 2nd and 3rd arguments are  the retrieval mode and contour simplification mode respectively. I'm not sure why it requires a .copy() of the image... maybe it tries to change it? 
contours = imutils.grab_contours(contours) #parse the output of findContours with Adrian (from PyImageSearch)'s fancy imutils library

# Get a list of the areas of all the contours (in preparation of picking the biggest one)
contour_areas = []
for contour in contours: 
	contour_areas.append(cv2.contourArea(contour)) #calculates the area of the contour

contour_areas.sort() #Sort all the contour areas from largest to smallest
wrench_area = contour_areas[len(contour_areas)-1] #get the last item (the largest) in the list. Note that len() returns the size (say, 5 elements) but the last element has index len()-1 (which would be 4)

print(wrench_area)
cv2.drawContours(image=image, contours=contours, contourIdx=-1, color=(0,255,0), thickness=2)
cv2.imshow('Image output',image)
#cv2.imshow('The thing that goes into the contour finder', thresh)
 
cv2.waitKey(0)
cv2.destroyAllWindows()

