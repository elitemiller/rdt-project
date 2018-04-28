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
            self.accepted = True
            # get data
            data = self.queue.get()
            # clone socket
            sock = self.proto.socket()
            # set new socket info
            sock.bind(self.proto.randomPort())
            sock.remoteAddr = data[0]
            sock.remotePort = data[1]
            sock.accepted = True
            return (self, (sock.remoteAddr, sock.remotePort))

    def connect(self, addr):
        # addr[0] = ip, addr[1] = port
        if self.connected:
            raise StreamSocket.AlreadyConnected
        if not self.bound:
            self.bind(self.proto.randomPort())
        self.connected = True
        #self.send(other stuff)
        self.proto.output(",".join((str(self.port), str(addr[1]), str(0), str(5), "ACK", "test-oneway")).encode(),addr[0])

    def send(self, data):
        if not self.connected:
            raise StreamSocket.NotConnected
        self.proto.output(data, self.remoteAddr)
        #self.deliver(data)
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
        self.ports[int(dstPort)].queue.put((rhost, int(srcPort)))
        self.ports[int(dstPort)].deliver(payload.encode())
        #if flag == 'SYN' or flag == 'SYNACK':
            #if dstPort not in self.conns:
                #self.listeningSocks[dstPort].queue.put((rhost, srcPort))
        pass

    # random port number
    def randomPort(self):
        rando_num = random.randint(51245, 64999)
        while(rando_num in self.ports):
            rando_num = random.randit(51245, 64999)
        return rando_num
