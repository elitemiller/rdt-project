import sys
import threading
import collections
import queue
from network import *
import random

IPPROTO_RDT = 0xfe

class RDTSocket(StreamSocket):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.port = None
        self.remoteAddr = None
        self.bound = False
        self.accepted = False
        self.connected = False
        self.listening = False
        self.queue = queue.Queue()
        # maybe sequence numbers later?
        # Other initialization here

    # Binds the socket to a local port
    # If the port is already in use by another socket,
    #    then this method should raie a Socket.AddressInUse.
    # If this is a connected stream socket, it should raise 
    #    StreamSocket.AlreadyConnected.
    def bind(self, port):
        # check for address in use
        if self.accepted or self.connected:
            raise StreamSocket.AlreadyConnected
        if self.listening or port in self.proto.ports:
            raise Socket.AddressInUse
        self.port = port
        self.proto.ports[self.port] = self
        self.bound = True

    def listen(self):
        if self.connected:
            raise StreamSocket.AlreadyConnected
        if not self.bound:
            raise StreamSocket.NotBound
        self.listening = True
        self.proto.listeningSocks[self.port] = self

    def accept(self):
        if not self.listening:
            raise StreamSocket.NotListening
        else:
            #self.accepted = True
            # get data
            data = self.queue.get()
            # clone socket
            sock = self.proto.socket()
            # set new socket info
            sock.bind(self.proto.randomPort())
            sock.remoteAddr = data[0]
            sock.remotePort = data[1][0]
            sock.accepted = True
            #print("\n" +data[1][4] + " received in accept from " + str(sock.remoteAddr) + ", "+ str(sock.remotePort))
            #print(data)
            if data[1][4] == "SYN":
                #print("\nSYNACK sent in accept from " + str(sock.proto.host.ip) + ", "+ str(sock.port))
                sock.proto.output(",".join((str(sock.port), str(sock.remotePort), "seq_num", "ack_num", "SYNACK", "")).encode(), sock.remoteAddr)
                check = sock.queue.get()
                #print(check)
                if check[1][4] == "ACK":
                    sock.connected = True
                    return (sock, (sock.remoteAddr, int(sock.remotePort)))

    def connect(self, addr):
        # addr[0] = ip, addr[1] = port
        if self.connected:
            raise StreamSocket.AlreadyConnected
        if not self.bound:
            self.bind(self.proto.randomPort())
        self.remoteAddr = addr[0]
        self.remotePort = addr[1]
        self.proto.output(",".join((str(self.port), str(addr[1]), "seq_num", "ack_num", "SYN", "")).encode(),addr[0])
        check = self.queue.get()
        #print(check[4] + "in connect")
        #print("\n" +check[4] + " received in connect for " + str(self.proto.host.ip) + ", "+ str(self.port))
        if check[1][4] == "SYNACK":
            self.remotePort = check[1][0]
            self.proto.output(",".join((str(self.port), str(check[1][0]), "seq_num", "ack_num", "ACK", "")).encode(), addr[0])
            self.connected = True

    def send(self, data):
        if not self.connected:
            raise StreamSocket.NotConnected
        self.proto.output(",".join((str(self.port), str(self.remotePort), "seq_num", "ack_num", ",")).encode()+data, self.remoteAddr)
        #print(data)
        #self.deliver(data)

class RDTProtocol(Protocol):
    PROTO_ID = IPPROTO_RDT
    SOCKET_CLS = RDTSocket

    # Initialize a new instance of the protocol on the given host
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conns = {}
        self.ports = {}
        self.listeningSocks = {}
        # Other initialization here

    # Called when a segment is received for this protocol from
    #    the given source address.
    # This method should perform demultiplexing to determine
    #    the appropriate socket, then pass the segment and the 
    #    source address to the input() method on that socket.
    def input(self, seg, rhost):
        data = seg.decode().split(",", 5)
        #print(data)
        #print("help")
        srcPort = data[0]
        dstPort = data[1]
        seqNum = data[2]
        ackNum = data[3]
        flag = data[4]
        payload = data[5]
        #print("\n" +data[4] + " received in input from " + str(rhost) + ", "+ str(srcPort))
        if flag == 'SYN' or flag == 'SYNACK' or flag == 'ACK':
            self.ports[int(dstPort)].queue.put((rhost, data))
        else:
            #print("no ACKs")
            self.ports[int(dstPort)].deliver((data[5]).encode())
        #self.ports[int(dstPort)].deliver(payload.encode())
            #if dstPort not in self.conns:
                #self.listeningSocks[dstPort].queue.put((rhost, srcPort))

    # random port number
    def randomPort(self):
        rando_num = random.randint(51245, 64999)
        while(rando_num in self.ports):
            rando_num = random.randit(51245, 64999)
        return rando_num
