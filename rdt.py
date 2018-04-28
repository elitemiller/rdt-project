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
            self.accepted = True
            # get data
            #data = self.queue.get()
            # clone socket
            #sock = self.proto.socket()
            # set new socket info
            #sock.bind(self.port)
            #sock.remoteAddr = data[0]
            #sock.remotePort = data[1]
            #sock.accepted = True
            return (self, (1, 2))

    def connect(self, addr):
        # addr[0] = ip, addr[1] = port
        if self.connected:
            raise StreamSocket.AlreadyConnected
        self.connected = True
        #self.send(other stuff)
        print(addr)
        self.output(b'stuff', addr)

    def send(self, data):
        if not self.connected:
            raise StreamSocket.NotConnected
        #self.proto.output(stuff)
        pass

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
        srcPort = data[0]
        dstPort = data[1]
        seqNum = data[2]
        ackNum = data[3]
        flag = data[4]
        payload = data[5]
        if flag == 'SYN' or flag == 'SYNACK':
            if dstPort not in self.conns:
                self.listeningSocks[dstPort].queue.put((rhost, srcPort))

