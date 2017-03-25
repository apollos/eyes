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

#class ServerWorker(threading.Thread):
class ServerWorker():
    """ServerWorker"""
    def __init__(self, client_id, broker_ip, broker_port):
        #threading.Thread.__init__ (self)
        self.id = client_id
        self.broker_port = broker_port
        self.broker_ip = broker_ip

    def run(self):
        context = zmq.Context()
        socket = context.socket(zmq.DEALER)
        socket.connect('tcp://%s:%d' % (self.broker_ip, self.broker_port))
        tprint('Worker [%d] started' % (self.id))
        idPattern= re.compile(r'\d+')
        while True:
            try:
                ident, msg = socket.recv_multipart()
                idnum = idPattern.findall(ident)
                #tprint('Worker [%d] received %s from [%s]' % (self.id, msg, ident))                
                targetAddr = u'Stream-out-%s' % idnum[0]
                socket.send_multipart([targetAddr.encode('ascii'), msg])
                #tprint('Worker [%d] send %s to [%s]' % (self.id, msg, targetAddr))
            except KeyboardInterrupt:
                print ("ctrl+c received, quit")
                break
            
        socket.close()
        context.term()


def main(ip, port):
    """main function"""
    seed(datetime.now())
    client_id = int(random()*1000)
    server = ServerWorker(client_id, ip, port)
    server.run()
    #server.join()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='zmq_eyes is the worker of detection program')

    parser.add_argument('-t', "--broker_ip", action="store", help="Specify the broker IP, default is localhost", default="localhost", dest="broker_ip")
    parser.add_argument('-p', "--broker_port", action="store", help="Specify the broker Port, default is 5571", default=5571, type=int, dest="broker_port")
    results = parser.parse_args()
    main(results.broker_ip, results.broker_port)
