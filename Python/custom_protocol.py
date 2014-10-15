from twisted.internet.protocol import Protocol
from twisted.internet.protocol import Factory

from twisted.application.service import Application
from twisted.application import service, internet

from twisted.internet import reactor

class CustomProtocol (Protocol):
  def __init__(self, factory):
    self.factory = factory

  def connectionMade(self):
    self.factory.numProtocols = self.factory.numProtocols+1
    self.transport.write("Welcome! There are currently %d open connections.\n" %
            (self.factory.numProtocols))

  def connectionLost(self, reason):
    self.factory.numProtocols = self.factory.numProtocols-1

  def dataReceived(self, data):
    self.transport.write(data)

class CustomProtocolFactory (Factory):
  def __init__ (self):
    self.numProtocols = 0
  def buildProtocol (self, addr):
    return CustomProtocol(self)

#start web frontend...
application = service.Application("web_FrEnd")
webservice = internet.TCPServer(9909, CustomProtocolFactory())

webservice.setServiceParent(application)

webservice.startService()

#reactor.run()
