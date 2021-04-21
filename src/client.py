# import the necessary packages
from imutils.video import VideoStream
import imagezmq
import argparse
import socket
import time
import signal
# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-s", "--server-ip", required=True,
	help="ip address of the server to which the client will connect")
args = vars(ap.parse_args())
# initialize the ImageSender object with the socket address of the
# server
sender = imagezmq.ImageSender(connect_to="tcp://{}:5555".format(
	args["server_ip"]))
# get the host name, initialize the video stream, and allow the
# camera sensor to warmup
rpiName = socket.gethostname()
#vs = VideoStream(usePiCamera=True).start()
vs = VideoStream(src=0).start()
time.sleep(2.0)

class Patience:
    """Timing class using system ALARM signal.
    When instantiated, starts a timer using the system SIGALRM signal. To be
    used in a with clause to allow a blocking task to be interrupted if it
    does not return in specified number of seconds.
    See main event loop in Imagenode.py for Usage Example
    Parameters:
        seconds (int): number of seconds to wait before raising exception
    """
    class Timeout(Exception):
        pass

    def __init__(self, seconds):
        self.seconds = seconds

    def __enter__(self):
        signal.signal(signal.SIGALRM, self.raise_timeout)
        signal.alarm(self.seconds)

    def __exit__(self, *args):
        signal.alarm(0)    # disable alarm

    def raise_timeout(self, *args):
        raise Patience.Timeout()
while True:
	# read the frame from the camera and send it to the server
	frame = vs.read()

	#frame = imutils.resize(frame, width=320)
	try:
		with Patience(3):
			sender.send_image(rpiName, frame)
	except Patience.Timeout:
		print("reconnecting...")
		sender.zmq_socket.close()
		sender.zmq_context.term()
		sender = imagezmq.ImageSender(connect_to="tcp://{}:5555".format(
			args["server_ip"]))