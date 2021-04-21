# import the necessary packages
from imutils import build_montages
from datetime import datetime
import numpy as np
import imagezmq
import argparse
import imutils
import cv2
# construct the argument parser and parse the arguments
# No need for this for now!
"""
ap = argparse.ArgumentParser()
ap.add_argument("-mW", "--montageW", required=True, type=int,
	help="montage frame width")
ap.add_argument("-mH", "--montageH", required=True, type=int,
	help="montage frame height")
args = vars(ap.parse_args())
"""
# initialize the ImageHub object
imageHub = imagezmq.ImageHub()

frameDict = {}
# initialize the dictionary which will contain  information regarding
# when a device was last active, then store the last time the check
# was made was now
lastActive = {}
lastActiveCheck = datetime.now()
# stores the estimated number of Pis, active checking period, and
# calculates the duration seconds to wait before making a check to
# see if a device was active
ESTIMATED_NUM_PIS = 1
ACTIVE_CHECK_PERIOD = 0.5
ACTIVE_CHECK_SECONDS = ESTIMATED_NUM_PIS * ACTIVE_CHECK_PERIOD
# assign montage width and height so we can view all incoming frames
# in a single "dashboard"
#mW = args["montageW"]
#mH = args["montageH"]
mW = 400
mH = 400
fourcc = cv2.VideoWriter_fourcc('X','V','I','D')
#fourcc = cv2.VideoWriter_fourcc(*'MPEG')
#fourcc = cv2.VideoWriter_fourcc('M','P','E','G')
#fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v') # note the lower case
started= False
 
counter =500
# start looping over all the frames
while True:
	print(datetime.now())
	# receive RPi name and frame from the RPi and acknowledge
	# the receipt
	(rpiName, frame) = imageHub.recv_image()
	imageHub.send_reply(b'OK')
	# if a device is not in the last active dictionary then it means
	# that its a newly connected device
	if rpiName not in lastActive.keys():
		print("[INFO] receiving data from {}...".format(rpiName))
	# record the last active time for the device from which we just
	# received a frame
	lastActive[rpiName] = datetime.now()
	#frame = imutils.resize(frame, width=400,height=400)

	(h, w) = frame.shape[:2]
	if(not started):
		out = cv2.VideoWriter('project.avi',fourcc, 60, (w,h))
		started= True
	frameDict[rpiName] = frame
	"""
	# build a montage using images in the frame dictionary
	montages = build_montages(frameDict.values(), (w, h), (mW, mH))
	# display the montage(s) on the screen
	for (i, montage) in enumerate(montages):
		cv2.imshow("screen({})".format(i),montage)
	"""
	cv2.imshow("screen",frame)
	#frame = cv2.resize(frame,(400,400))
	if(counter >0):
		out.write(frame)
		counter -= 1
	if(counter== 0):
		out.release()
		counter = -1
	print(counter)
	# detect any kepresses
	key = cv2.waitKey(1) & 0xFF
	if (datetime.now() - lastActiveCheck).seconds > ACTIVE_CHECK_SECONDS:
		# loop over all previously active devices
		for (rpiName, ts) in list(lastActive.items()):
			# remove the RPi from the last active and frame
			# dictionaries if the device hasn't been active recently
			if (datetime.now() - ts).seconds > ACTIVE_CHECK_SECONDS:
				print("[INFO] lost connection to {}".format(rpiName))
				lastActive.pop(rpiName)
				frameDict.pop(rpiName)
		# set the last active check time as current time
		lastActiveCheck = datetime.now()
	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break
# do a bit of cleanup
cv2.destroyAllWindows()