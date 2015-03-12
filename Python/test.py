from networkInterface import NetworkInterface 
import sys

from twisted.python import log
log.startLogging(sys.stdout)

x = NetworkInterface()

fromPort = int(sys.argv[1])
toPort = int(sys.argv[2])


    
#action = raw_input("What to do [g]et K or [s]et K V :")
#command = action.split()

#print "command received: ", command
if sys.argv[3] == "g":
    x.connect(fromPort,toPort).addCallback(x.get,"key1")

elif sys.argv[3] == "s":
    x.connect(fromPort,toPort).addCallback(x.set,"key1", sys.argv[4])
        
from twisted.internet import reactor
reactor.run()


