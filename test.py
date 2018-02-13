from socketIO_client_nexus import SocketIO, LoggingNamespace
import time
from random import *


with SocketIO('13.125.124.80', 3000, LoggingNamespace) as socketIO:
    while True:
        socketIO.emit('heartbeat',str(randint(60, 120)))
        time.sleep(1);
    socketIO.wait(seconds=1)
