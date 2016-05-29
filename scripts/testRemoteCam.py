import sys
import cv2  
import numpy
import cv2.cv as cv
import socket


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python testRemoteCam.py <target ip> <port>")
        exit(-1)
    CAMIDX = 0
    capture = cv2.VideoCapture(CAMIDX)  
    if not capture.isOpened():
        print("Can not open Cam!")
        exit(-1)
    capture.set(cv.CV_CAP_PROP_FRAME_WIDTH, 640)  
    capture.set(cv.CV_CAP_PROP_FRAME_HEIGHT, 480)  
    cv2.namedWindow("camera_Capture")  
      
    HOST = sys.argv[1]
    PORT = sys.argv[2]
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    sock.connect((HOST, int(PORT)))  
    print "Host %s connected\n" % (HOST)
    encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),85]
    
    while True:  
        ret, img = capture.read()
        result, imgencode = cv2.imencode('.jpg', img, encode_param)
        data = numpy.array(imgencode)
        stringData = data.tostring()
        print len(stringData)
        
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
