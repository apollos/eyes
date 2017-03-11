import zmq
import sys
import threading
import time
from random import randint, random, seed
import re
import argparse
from datetime import datetime


def tprint(msg):
    """like print, but won't get newlines confused with multiple threads"""
    sys.stdout.write(msg + '\n')
    sys.stdout.flush()

#class ServerTask(threading.Thread):
class ServerTask():
    """ServerTask"""
    def __init__(self, in_port, out_port):
        #threading.Thread.__init__ (self)    
        self.in_port = in_port
        self.out_port = out_port

    def run(self):
        context = zmq.Context()
        frontend = context.socket(zmq.ROUTER)
        frontend.bind('tcp://*:%d' % (self.in_port))

        backend = context.socket(zmq.DEALER)
        backend.bind('tcp://*:%d' % (self.out_port))
        print("Start Broker")
        try:
            zmq.proxy(frontend, backend)
        except KeyboardInterrupt:
            print ("ctrl+c received, quit")
        finally:
            frontend.close()
            backend.close()
            context.term()


def main(in_port, out_port):
    """main function"""
    server = ServerTask(in_port, out_port)
    server.run()
    #server.join()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='zmq_broker is the router for all streams')

    parser.add_argument('-i', "--stream_in", action="store", help="Specify the port of stream in data, default is 5570", default=5570, type=int, dest="in_port")
    parser.add_argument('-o', "--stream_out", action="store", help="Specify the Port of stream out data, default is 5571", default=5571, type=int, dest="out_port")
    results = parser.parse_args()
    main(results.in_port, results.out_port)
