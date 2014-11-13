from twisted.internet.protocol import Protocol, Factory, ClientFactory
from twisted.internet import reactor

class CloudComms(Protocol):

    def connectionMade(self):
        self.transport.write("connected")
        self.factory.clients.append(self)
        print "clients are ", self.factory.clients
        self.ctr = 0

    def connectionLost(self, reason):
        #self.factory.clients.remove(self)
        print 'Lost connection.  Reason:', reason

    def dataReceived(self, data):
        print("Receiving Data from %s" % self.transport.getPeer())
        print "data is ", data
        print self.ctr
        if(data == "connected"):
            self.message("ping")
        if("ping" in data and self.ctr < 25):
            self.message("pong")
            self.ctr+=1
        elif("pong" in data and self.ctr < 25):
            self.message("ping")

    def message(self, message):
        self.transport.write(message + '\n')

class CloudClientFactory(ClientFactory):

    protocol = CloudComms

    def __init__(self, deferred):
        self.deferred = deferred
        self.clients = []

    def startedConnecting(self, connector):
        print 'Started to connect.'

    def buildProtocol(self, addr):
        print 'Connected.'
        proto = ClientFactory.buildProtocol(self, addr)
        return proto

    def clientConnectionLost(self, connector, reason):
        print 'Lost connection.  Reason:', reason
        if self.deferred is not None:
            d, self.deferred = self.deferred, None
            d.errback(reason)

    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed. Reason:', reason
        if self.deferred is not None:
            d, self.deferred = self.deferred, None
            d.errback(reason)
