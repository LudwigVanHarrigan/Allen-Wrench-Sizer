# Allen-Wrench-Sizer
A computer vision allen wrench size measurer.

It can detect the size of an allen wrench with a webcam a fixed distance above a backlit surface.
This software is purely experimental at this point; I consider WrenchLocalAreaMeasure.py to be the most developed sandbox.


This is also my first time really using Git and GitHub, so don't judge my practices too harshly :)

## How to run

1. Use Linux. Otherwise you won't be able to use my built in preset for Guvcview. If you want to use Windows, download the Logitech camera settings app and use it to make the allen wrench image look like the example images in this repo. You'll have to calibrate the pixels per mm value.
2. Ensure python 3 is installed.
3. In a virtual environment, install required Python packages `opencv-python imutils numpy scipy` and any others it yells at you about when you try to run it.
4. Run it! If you're using Linux, your webcam might be on /dev/video0, /dev/video1, /dev/video2, or any number of other /dev/video*. Find in the code where the path to the camera is defined and set it to the Wrench Whisperer's camera.
5. You may need to recalibrate it. In the while(True) that is the main program, there is a print statement `#print(pxAcross)`. Uncomment it. Probably comment out the other print statement below it. Measure allen wrenches of known size, and make an Excel sheet plotting actual size vs pixels across. Create a best fit line. Insert this equation into the `pxToMM()` function definition.
  

Happy wrench whispering!
