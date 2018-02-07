from socketIO_client_nexus import SocketIO, LoggingNamespace
import time
from random import *


with SocketIO('127.0.0.1', 3000, LoggingNamespace) as socketIO:
    while True:
        socketIO.emit('heartbeat',str(randint(60, 120)))
        time.sleep(1);
    socketIO.wait(seconds=1)
