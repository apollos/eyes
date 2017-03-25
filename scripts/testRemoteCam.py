import sys
import cv2  
import numpy
import cv2.cv as cv
import socket
import os
import struct


if __name__ == "__main__":
    if len(sys.argv) < 3 or len(sys.argv) > 5:
        print("Usage: python testRemoteCam.py <target ip> <port> [video file] [start pos percentage]")
        exit(-1)
    if len(sys.argv) > 3:
        videoPath = sys.argv[3]
        if len(sys.argv) == 5:
            percentagePos = int(sys.argv[4])
        else:
            percentagePos = 0
        if not os.path.exists(videoPath):
            print("Can not open %s!" % videoPath)
            exit(-1)
        capture = cv2.VideoCapture(videoPath)  
        count = capture.get(cv.CV_CAP_PROP_FRAME_COUNT); 
        if percentagePos == 0:
            capture.set(cv.CV_CAP_PROP_POS_FRAMES,0); 
        else:
            capture.set(cv.CV_CAP_PROP_POS_FRAMES,int(count/percentagePos)); 
    else:
        CAMIDX = 0
        capture = cv2.VideoCapture(CAMIDX)  
<<<<<<< HEAD
        capture.set(cv.CV_CAP_PROP_FRAME_WIDTH, 640*0.8)  
        capture.set(cv.CV_CAP_PROP_FRAME_HEIGHT, 480*0.8)
=======
        capture.set(cv.CV_CAP_PROP_FPS, 30);
        capture.set(cv.CV_CAP_PROP_FRAME_WIDTH, 1024)  
        capture.set(cv.CV_CAP_PROP_FRAME_HEIGHT, 768) 
>>>>>>> devbranch
    if not capture.isOpened():
        print("Can not open Cam!")
        exit(-1)
    #cv2.namedWindow("camera_Capture", cv.CV_WINDOW_AUTOSIZE)  
      
    HOST = sys.argv[1]
    PORT = sys.argv[2]
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    
    sock.connect((HOST, int(PORT)))  
    print "Host %s connected\n" % (HOST)
    #get image size
    ret, img = capture.read()
    high, width, channel = img.shape
    handshake='SEND'
    packStr = '!%ds3I' % len(handshake)
    sndStr = struct.pack(packStr,handshake,high, width, channel)
    print sndStr
    bytes = sock.send( sndStr.ljust(16) );
    
    encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),75]
    #dim = (640, 480)
    while True:  
        ret, img = capture.read()
        
        if(not ret):
            capture.set(cv.CV_CAP_PROP_POS_FRAMES,int(count/percentagePos));
            continue
        
        #img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
        result, imgencode = cv2.imencode('.jpg', img, encode_param)
        data = numpy.array(imgencode)
        stringData = data.tostring()
        
        try:  
            bytes = sock.send( str(len(stringData)).ljust(16));
            bytes += sock.send( stringData );
            print "Send %d bytes!" % (bytes)
        except Exception as ex:  
            print "Destination connection broken"
            break
        except KeyboardInterrupt:  
            print "Interrupted!"  
            break
        
        #time.sleep(0.1)  
        cv2.imshow("camera_Capture", img)  
        if cv2.waitKey(50) == 122:  
            break  
          
    sock.close()
    cv2.destroyAllWindows() 
