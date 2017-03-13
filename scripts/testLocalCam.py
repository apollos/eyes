import sys
import cv2  
import numpy
import cv2.cv as cv
import socket
import os
import struct


if __name__ == "__main__":
    if len(sys.argv) != 1:
        print("Usage: python testLocalCam.py")
        exit(-1)
    CAMIDX = 0
    capture = cv2.VideoCapture(CAMIDX)  
    if not capture.isOpened():
        print("Can not open Cam!")
        exit(-1)
    #cv2.namedWindow("camera_Capture", cv.CV_WINDOW_AUTOSIZE)  
    capture.set(cv.CV_CAP_PROP_FRAME_WIDTH, 640*0.8)  
    capture.set(cv.CV_CAP_PROP_FRAME_HEIGHT, 480*0.8)
    #get image size
    ret, img = capture.read()
    high, width, channel = img.shape
    print("%d - %d - %d\n", high, width, channel)
    
    encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),80]
    dim = (640, 480)
    while True:  
        ret, img = capture.read()
        
        if(not ret):
            capture.set(cv.CV_CAP_PROP_POS_FRAMES,int(count/percentagePos));
            continue
        
        img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
        
        #time.sleep(0.1)  
        cv2.imshow("camera_Capture", img)  
        if cv2.waitKey(50) == 122:  
            break  
          
    cv2.destroyAllWindows() 
