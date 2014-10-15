from entangled.kademlia import node
from twisted.internet.defer import Deferred
from twisted.internet.protocol import Protocol
import networkserviceapi
import sys

class OverlayNetworlProtocol (Protocol):
  def __init__ (self):
    print "init"

  def dataReceived (self, data):
    print "data_recieved"

  def connectionLost (self, reason=None):
    print "connection_lost"

def initialize(bootstrap_contact=None):
  """
  This function asks the user to provide the bootstrap contacts to make the net
  entry, if node provided when this script is executed.
  """

  d = Deferred()

  port = int(sys.argv[2])
  node_obj = node.Node(port)

  d.addCallback(node_obj.joinNetwork, bootstrap_contact)

  return d

def hello(self):
  print "Hello"

if __name__ == '__main__' :

  from twisted.internet import reactor

  # initialize node + enter the net.
  known_nodes = [("127.0.0.1",int(sys.argv[1]))]
  d = initialize(known_nodes)
  d.addCallback(hello)

  print "outside init"
  reactor.run()
