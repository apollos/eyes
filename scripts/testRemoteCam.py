import sys
import cv  
import time, socket, Image, StringIO  


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python testRemoteCam.py <target ip> <port>")
        exit(-1)
    CAMIDX = 0
    capture = cv.CaptureFromCAM(CAMIDX)  
    cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_WIDTH, 640)  
    cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_HEIGHT, 480)  
      
    HOST = sys.argv[1]
    PORT = sys.argv[2]
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    sock.connect((HOST, int(PORT)))  
    print "Host %s connected\n" % (HOST)
      
    while True:  
        img = cv.QueryFrame(capture)  
        pi = Image.fromstring("RGB", cv.GetSize(img), img.tostring())  
        buf = StringIO.StringIO()  
        pi.save(buf, format = "JPEG")  
        jpeg = buf.getvalue()  
        buf.close()  
        transfer = jpeg.replace("\n", "\-n")  
        print len(transfer), transfer[-1]  
        sock.sendall(transfer + "\n")  
        #time.sleep(0.1)  
        if cv.WaitKey(50) == 122:  
            break  
          
    sock.close()
