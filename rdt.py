import sys
import threading
import collections
import queue
from network import *

ports = queue.Queue(maxsize=45000)

IPPROTO_RDT = 0xfe

class RDTSocket(StreamSocket):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Other initialization here

    def bind(self, port):
        print(port)
        # check for address in use
        if (self, port) in ports.queue:
            raise Socket.AddressInUse
        self.port = port
        ports.put(self, port)

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Other initialization here

    def input(self, seg, rhost):
        pass
