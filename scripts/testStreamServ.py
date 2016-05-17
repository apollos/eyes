import socket, time  

if __name__ == "__main__":
    
    if len(sys.argv) != 3:
        print("Usage: python testStreamServ.py <my ip> <port>", file=sys.stderr)
        exit(-1)
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)  
    SOCKNUM = 2
    HOST = sys.argv[1]
    PORT = sys.argv[2]
    sock.bind((HOST, PORT))  
    sock.listen(SOCKNUM)  
      
    src, src_addr = sock.accept()  
    print "Source Connected by", src_addr  
      
    dst, dst_addr = sock.accept()  
    print "Destination Connected by", dst_addr  
      
    while True:  
        msg = src.recv(1024 * 1024)  
        #print len(msg)  
        if not msg:  
            break  
        try:  
            dst.sendall(msg)  
        except Exception as ex:  
            dst, dst_addr = sock.accept()  
            print "Destination Connected Again By", dst_addr  
        except KeyboardInterrupt:  
            print "Interrupted!"  
            break  
      
    src.close()  
    dst.close()  
    sock.close()
