import cv2
import cv2.cv as cv
import sys

try:
    vidFile = cv2.VideoCapture(sys.argv[1])
except:
    print "problem opening input stream"
    sys.exit(1)
if not vidFile.isOpened():
    print "capture stream not open"
    sys.exit(1)

#vidFile.set(cv.CV_CAP_PROP_FRAME_WIDTH, 640);
#vidFile.set(cv.CV_CAP_PROP_FRAME_HEIGHT, 480);

ret, frame = vidFile.read() # read first frame, and the return code of the function.
#cv2.resize(frame, frame, Size(640, 480), 0, 0, INTER_CUBIC);

dim = (640, 480)

while ret:  # note that we don't have to use frame number here, we could read from a live written file.
    resized = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)
    cv2.imshow("frameWindow", resized)
    cv2.waitKey(20) # time to wait between frames, in mSec
    ret, frame = vidFile.read() # read next frame, get next return code

cv2.destroyAllWindows() 
