import cv2.cv as cv  
import cv2
import socket, time, StringIO  
import sys
import numpy as np


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python testStreamClient.py <target ip> <port>")
        exit(-1)
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    sock.connect((HOST, PORT))      
    handshake='RCV'
    packStr = '!%dsiii' % len(handshake)
    sndStr = struct.pack(packStr,handshake,0, 0, 0)
    bytes = sock.send( str(len(sndStr)).ljust(16));
    bytes += sock.send( stringData );	
    cv2.namedWindow("DetectResult", cv.CV_WINDOW_AUTOSIZE)  
    #img = cv2.createImageHeader((640, 480), cv.IPL_DEPTH_8U, 3)  
      
    while True:        
        rcvLen = 0
        DataValue = ''
        erroFlag = 0
        while len(DataValue) < 16:
            packet = sock.recv(16 - len(DataValue))
            if not packet:
                print "RCV Data Len Error!!!"
                erroFlag = 1
                break;
            DataValue += packet
        if erroFlag == 1:
            break;
        DataLen = int(DataValue.strip("\x00"))
        print "Rcv %d" % (DataLen)
        DataValue = ''
        while len(DataValue) < DataLen:
            packet = sock.recv(DataLen - len(DataValue))
            if not packet:
                print "RCV Data Error!!!"
                erroFlag = 1
                break;
            DataValue += packet
        if erroFlag == 1:
            break;
        #uncompress
        buff = np.fromstring(DataValue, dtype='uint8')
        img = cv2.imdecode(buff, cv2.CV_LOAD_IMAGE_COLOR);
        #cv.SetData(img, DataValue)  
        cv2.imshow("DetectResult", img)  
        if cv2.waitKey(10) == 122:  
            break  
      
    sock.close()  
    cv2.destroyAllWindows()
