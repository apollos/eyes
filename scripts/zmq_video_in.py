import zmq
import sys
import threading
import time

import argparse

import signal
import cv2
import cv2.cv as cv
import numpy as np
import os

def tprint(msg):
    """like print, but won't get newlines confused with multiple threads"""
    sys.stdout.write(msg + '\n')
    sys.stdout.flush()

#class ClientTask(threading.Thread):
class ClientTask():
    """ClientTask"""
    def __init__(self, id, ip, port, cam_idx, v_path):
        self.id = id
        self.ip = ip
        self.port = port
        self.cam_idx = cam_idx
        self.video_path = v_path
        #threading.Thread.__init__ (self)

    def run(self):
        context = zmq.Context()
        socket = context.socket(zmq.DEALER)
        identity = u'Stream-in-%d' % self.id
        socket.identity = identity.encode('ascii')
        socket.connect('tcp://%s:%d' % (self.ip, self.port))
        tprint('Client [%d] started' % (self.id))
        reqs = 0
        cv2.namedWindow("camera_Capture", cv.CV_WINDOW_NORMAL) 
        if(self.video_path == None or self.video_path == ""):
            videInfo = VideoCapture(camIdx=self.cam_idx, fps=15, quality=80)
        else:
            videInfo = VideoCapture(videoPath = self.video_path, quality=75)
        if (videInfo.setProperty()):
            while True:
                reqs = reqs + 1
                imgData, showImg = videInfo.getImage()
                if (not imgData is None):
                    try:
                        socket.send(imgData)
                        cv2.imshow("camera_Capture", showImg)
                        if(videInfo.getInputKey()):
                            break
                    except KeyboardInterrupt:
                        print ("ctrl+c received, quit")
                        break
                else:
                    break
        socket.close()
        context.term()
        cv2.destroyAllWindows() 

class VideoCapture():
    def __init__(self, camIdx=-1, firstFrame=None, fps=25, w=640, h=480, quality=100, videoPath=None):
        self.camIdx = camIdx
        self.firstFrame = firstFrame
        self.fps = fps
        self.w = w
        self.h = h
        self.quality = quality
        self.encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),self.quality]
        self.videoPath = videoPath
        self.frameCount = 0
        
    
    def getImage(self):
        
        try:
            ret, img = self.camera.read()    
            if(not ret):
                self.camera.set(cv.CV_CAP_PROP_POS_FRAMES,0);
                ret, img = self.camera.read() 
        except KeyboardInterrupt:
            print ("ctrl+c received, quit")
            return None 
        dim = (self.w, self.h)
        try:
            img = cv2.resize(img, dim, interpolation = cv2.INTER_CUBIC)
            result, imgencode = cv2.imencode('.jpg', img, self.encode_param)
        except BaseException:
            return None
        data = np.array(imgencode)
        #stringData = data.tostring()
        return data, img

    def getInputKey(self):
        if cv2.waitKey(int(1000/self.fps)) & 0xff == ord('q'):  
            return True
        return False  

    def setProperty(self):
        if(self.camIdx != -1):
            print ("Open local cam %d" % (self.camIdx))
            self.camera = cv2.VideoCapture(self.camIdx)
        elif(self.videoPath):
            if ((self.videoPath.find("http") >= 0) or (self.videoPath.find("https") >= 0)):
                print "Open remote IP cam %s" % (self.videoPath)
            else:
                if not os.path.exists(self.videoPath):
                    print("Can not open %s!" % (self.videoPath))
                    return False
                print ("Open video %s" % (self.videoPath))
            self.camera = cv2.VideoCapture(self.videoPath)  
            self.frameCount = self.camera.get(cv.CV_CAP_PROP_FRAME_COUNT); 
            self.camera.set(cv.CV_CAP_PROP_POS_FRAMES,0); 
            self.fps = self.camera.get(cv.CV_CAP_PROP_FPS);
            #cv2.CreateTrackbar("Position", windowName, value, count, onChange)
        else:
            print "camIdx %d" %(self.camIdx)
            return False
        if not self.camera.isOpened():
            print("Can not open Cam %d!", self.camIdx)
            return False
        #self.camera.set(cv.CV_CAP_PROP_FPS, self.fps);
        self.camera.set(cv.CV_CAP_PROP_FRAME_WIDTH, self.w)  
        self.camera.set(cv.CV_CAP_PROP_FRAME_HEIGHT, self.h)         
        return True 
        

def main(client_id, ip, port, cam_idx, v_path):
    """main function"""

    client = ClientTask(client_id, ip, port, cam_idx, v_path)
    client.run()
    #client.join()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='zmq_video_in is the client to capture the video')

    parser.add_argument('-t', "--broker_ip", action="store", help="Specify the broker IP, default is localhost", default="localhost", dest="broker_ip")
    parser.add_argument('-p', "--broker_port", action="store", help="Specify the broker Port, default is 5570", default=5570, type=int, dest="broker_port")
    parser.add_argument('-c', "--cam_id", action="store", help="Specify the local camera idx", default=0, type=int, dest="cam_idx")
    parser.add_argument('-l', "--video_location", action="store", help="Specify the input video full path", dest="video_path")
    parser.add_argument('-i', "--client_id", action="store", help="Specify the client id and it shall be pair with stream in", required=True, type=int, dest="client_id")
    results = parser.parse_args()
    main(results.client_id, results.broker_ip, results.broker_port, results.cam_idx, results.video_path)
