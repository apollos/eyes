import zmq
import sys
import threading
import time

import argparse

import signal
import cv2.cv as cv  
import cv2
import numpy


def tprint(msg):
    """like print, but won't get newlines confused with multiple threads"""
    sys.stdout.write(msg + '\n')
    sys.stdout.flush()

#class ClientTask(threading.Thread):
class ClientTask():
    """ClientTask"""
    def __init__(self, id, ip, port):
        self.id = id
        self.broker_port = port
        self.broker_ip = ip
        #threading.Thread.__init__ (self)

    def run(self):
        context = zmq.Context()
        socket = context.socket(zmq.DEALER)
        identity = u'Stream-out-%d' % self.id
        socket.identity = identity.encode('ascii')
        socket.connect('tcp://%s:%d' % (self.broker_ip, self.broker_port))
        tprint('Client2 [%d] started' % (self.id))
        cv2.namedWindow("DetectResult", cv.CV_WINDOW_NORMAL)  
        while True:            
            try:
                msg = socket.recv()
                imgData = numpy.fromstring(msg, dtype='uint8')    
                img = cv2.imdecode(imgData, cv2.CV_LOAD_IMAGE_COLOR);
                #cv.SetData(img, DataValue)  
                cv2.imshow("DetectResult", img)  
                if cv2.waitKey(10) & 0xff == ord('q'):  
                    break  
            except KeyboardInterrupt:
                print ("ctrl+c received, quit")
                break
            #print("%s: Recv msg [%s]" % (identity, msg))
        socket.close()
        context.term()
        cv2.destroyAllWindows()

def main(client_id, ip, port):
    """main function"""

    client = ClientTask(client_id, ip, port)
    client.run()
    #client.join()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='zmq_video_out is the client to show video')

    parser.add_argument('-t', "--broker_ip", action="store", help="Specify the broker IP, default is localhost", default="localhost", dest="broker_ip")
    parser.add_argument('-p', "--broker_port", action="store", help="Specify the broker Port, default is 5570", default=5570, type=int, dest="broker_port")
    parser.add_argument('-i', "--client_id", action="store", help="Specify the client id and it shall be pair with stream in", required=True, type=int, dest="client_id")
    results = parser.parse_args()
    main(results.client_id, results.broker_ip, results.broker_port)
