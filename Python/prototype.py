from entangled.kademlia import node
from twisted.internet.defer import Deferred
from twisted.internet import defer
from twisted.internet.protocol import Protocol

from twisted.application.service import Application
from twisted.application import service, internet

import networkserviceapi
import custom_protocol
import sys, re

from twisted.internet import stdio
from twisted.protocols import basic


class UserInputBot(basic.LineReceiver):
    from os import linesep as delimiter

    def __init__ (self, node_obj):
        self.node = node_obj


    def connectionMade(self):
        self.transport.write('>>> Use this program by calling any of the following: \n')
        self.transport.write('a) findService service_name\n')
        self.transport.write('b) postService service_name provider_ip provider_port\n')
        self.transport.write('c) printContacts \n')
        self.transport.write('d) launchApp app_name \n')
        self.transport.write('e) joinApp app_name \n')
        self.transport.write('>>> ')


    def lineReceived(self, line):
        if 'findService' in line:
          self.sendLine('Find that service!')

          line = line.split()

          service_name = line[1]

          result = networkserviceapi.findService(self.node, service_name)

        elif 'postService' in line:
          self.sendLine('Post that service!')

          line = line.split()

          service = networkserviceapi.Service(line[1],"description", line[2], line[3])

          result = networkserviceapi.postService(self.node, service)

        elif line == 'printContacts':
          self.node.printContacts()
          result = ""

        elif 'launchApp' in line:
          self.sendLine('Launch that app!')

          line = line.split()

          app_name = line [1]

          # Create the application
          application = Application(app_name)

          # add calling node to the pool of nodes for that app
          application.addNode(self.node)

          # launch it
          application.launchApp(self.node)

          result = application


        elif 'joinApp' in line:
          self.sendLine('Join that app!')

          line = line.split()

          app_name = line [1]

          # find the applicaiton obejct in the DHT.
          result = findApplication(self.node, app_name)

          # if found add node.
          result.addCallback(joinApplication, self.node)

          # then reprint showing you have joined this app
          result.addCallback(print_result, app_name)


        self.transport.write('>>> ')

        return result

def initialize(bootstrap_contact=None):
  """
  This function asks the user to provide the bootstrap contacts to make the net
  entry, if node provided when this script is executed.
  """

  port = int(sys.argv[1])
  node_obj = node.Node(port)

  node_obj.joinNetwork(bootstrap_contact)

  return node_obj

if __name__ == '__main__' :

  from twisted.internet import reactor

  known_nodes = [("127.0.0.1",int(sys.argv[2]))]

  # initialize node + enter the net.
  global node_object
  node_object = initialize(known_nodes)

  # launch the interactive mode
  stdio.StandardIO(UserInputBot(node_object))

  reactor.run()
