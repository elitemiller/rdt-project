import sys
import threading
import collections
import queue
from network import *

IPPROTO_RDT = 0xfe

class RDTSocket(StreamSocket):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.port = None
        self.remoteAddr = None
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
        if self.remoteAddr != None:
            raise StreamSocket.AlreadyConnected
        # check for address in use
        if port in self.proto.ports:
            raise Socket.AddressInUse
        self.port = port
        self.proto.ports.append(port)

    def listen(self):
        if self.port == None:
            raise StreamSocket.NotBound
        if self.remoteAddr != None:
            raise StreamSocket.AlreadyConnected
        self.listening = True
        self.proto.listeningSocks.append((self,self.port))

    def accept(self):
        if not self.listening:
            raise StreamSocket.AlreadyConnected
        else:
            # get data
            data = self.queue.get()
            # clone socket
            sock = self.proto.socket()
            # set new socket info
            sock.port = self.port
            sock.remoteAddr = data[0]
            sock.remotePort = data[1]

    def connect(self, addr):
        # addr[0] = ip, addr[1] = port
        if self.remoteAddr != None:
            raise StreamSocket.AlreadyConnected
        pass

    def input(self, seg, src):
        pass

    def send(self, data):
        pass

class RDTProtocol(Protocol):
    PROTO_ID = IPPROTO_RDT
    SOCKET_CLS = RDTSocket

    # Initialize a new instance of the protocol on the given host
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conns = {}
        self.ports = []
        self.listeningSocks = []
        # Other initialization here

    # Called when a segment is received for this protocol from
    #    the given source address.
    # This method should perform demultiplexing to determine
    #    the appropriate socket, then pass the segment and the 
    #    source address to the input() method on that socket.
    def input(self, seg, rhost):
        data = seg.decode().split(",", 5)
        srcPort = data[0]
        dstPort = data[1]
        seqNum = data[2]
        ackNum = data[3]
        flag = data[4]
        payload = data[5]
        if flag == 'SYN' or flag == 'SYNACK':
            if dstPort not in self.conns:
                pass

