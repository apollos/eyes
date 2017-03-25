import socket, time  
import sys
import cv2
import numpy

mySock = 0
srcSock = 0
dstSock = 0

def startServer():
    global mySock
    global srcSock
    global dstSock
    mySock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)  
    SOCKNUM = 2
    HOST = "0.0.0.0"
    PORT = 9119
    mySock.bind((HOST, PORT))  
    mySock.listen(SOCKNUM)  
    print "Start Server!"
    srcSock, src_addr = mySock.accept()  
    print "Source Connected by", src_addr  
      
    #dstSock, dst_addr = mySock.accept()  
    #print "Destination Connected by", dst_addr
    return 0

def closeServer():
    global mySock
    global srcSock
    global dstSock
    srcSock.close()  
    mySock.close()  
    #dstSock.close()
    return 0

def transferData():
    global mySock
    global srcSock
    global dstSock
    msg = srcSock.recv(1024 * 1024)  
    print len(msg)  
    if not msg:  
        return -1  
    try:  
        dstSock.sendall(msg)  
    except Exception as ex:  
        #dst, dst_addr = sock.accept()  
        #print "Destination Connected Again By", dst_addr  
        print "Destination connection broken"
        return -1
    except KeyboardInterrupt:  
        print "Interrupted!"  
        return -1
    return 0  

def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf

def readData():
    global mySock
    global srcSock

    length = recvall(srcSock,16)
    stringData = recvall(srcSock, int(length))
    if length == None or stringData == None:
        return None
    data = numpy.fromstring(stringData, dtype='uint8')    
    print length
    print data
    #cv.ShowImage("camera_Detect", img)  
    return data



if __name__ == "__main__":
    
    if len(sys.argv) != 1:
        print("Usage: python testStreamServ.py ")
        exit(-1)
    startServer()    
    cv2.namedWindow("camera_Detect")  
    while True:  
        #rst = transferData()
        data = readData()        
        if(data == None):
            break;
        decimg=cv2.imdecode(data,1)   
        cv2.imshow('camera_Detect',decimg)
        if cv2.waitKey(10) == 122:  
            break;             
    closeServer()
    cv2.destroyAllWindows()

