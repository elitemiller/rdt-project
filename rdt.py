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
        # Other initialization here

    # Binds the socket to a local port
    # If the port is already in use by another socket,
    #    then this method should raie a Socket.AddressInUse.
    # If this is a connected stream socket, it should raise 
    #    StreamSocket.AlreadyConnected.
    def bind(self, port):
        # check for address in use
        if port in self.proto.ports:
            raise Socket.AddressInUse
        self.port = port
        self.proto.ports.append(port)

    def listen(self):
        pass

    def accept(self):
        pass

    def connect(self, addr):
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
        # Other initialization here

    # Called when a segment is received for this protocol from
    #    the given source address.
    # This method should perform demultiplexing to determine
    #    the appropriate socket, then pass the segment and the 
    #    source address to the input() method on that socket.
    def input(self, seg, rhost):
        #self.sock.input(seg, src)
        pass

    # Hand the provided segment to the host's network layer
    # for delivery to this protocol on the destination host
    def output(self, seg, dst):
       pass


