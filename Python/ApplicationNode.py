from twisted.internet import stdio
from twisted.protocols import basic

class UserInputBot(basic.LineReceiver):
    from os import linesep as delimiter

    def __init__ (self, app_obj):
        self.app = app_obj


    def connectionMade(self):
        self.transport.write('>>> Use this program by calling any of the following: \n')
        self.transport.write('a) joinApp app_name\n')
        self.transport.write('b) printContacts \n')
        self.transport.write('>>> ')


    def lineReceived(self, line):
        if 'joinApp' in line:
          self.sendLine('Attempting to join app!')

          line = line.split()

          app_name = line[1]

          # join the application with the name provided
          result = self.app.joinApplication(app_name)

        elif line == 'printContacts':
          self.app._node.printContacts()
          result = ""

        elif line == "runApp":
          self.app.run()

          result = ""

        self.transport.write('>>> ')

        return result

class ApplicationNode (object):

  """
  This class represents an ApplicationNode which can be any type of process, except
  Web because only the Application deployer can be the WebProcess as of now.
  """

  global id_count
  id_count = 0

  def __init__(self):

      self._id = id_count + 1
      self._process = ""
      self._ip_address = "127.0.0.1"
      self._port = 4021

      # here is the logic to join the DHT, currently using an implementation of Kademlia
      from entangled.kademlia import node

      knownNodes = [("127.0.0.1", 4020)]

      self._node = node.Node(self._port)
      self._node.joinNetwork(knownNodes)


  def __str__(self):
      return "ApplicationNode: [id] = " + str(self._id) + " [ip_address] = " + str(self._ip_address) + " [port] = " + str(self._port)


  """
  Contains the logic to join an active Application in the cloud.
  """
  def joinApplication(self, app_name):
      """
      Joining an application in this context, consists
      of finding the "value": IP_Address in the DHT corresponding to the "key":
      app_name. Once found, start the communications between the application host
      and this client (ApplicationNode).
      """
      result = self._node.iterativeFindValue(app_name)

      result.addCallback(comms).addCallback(transmit_message)



      return result

  def joinFailure(self, app_name):
      print "ooops --> could not join application: ", app_name

      from twisted.internet import reactor
      reactor.stop()

  def print_contacts(self, arg):
        print "app_node --> printcontacts"
        self._node.printContacts()

        print "app_node --> printcontacts"

  def run(self):
      print "-run()-"
      # sleep for 1 second to enables the DHT to be up to date
      import time
      time.sleep(1)


      # [DEBUG] print contacts to show whether or not we are part of the DHT
      self._node.printContacts()
      print "-end of run()-"

def print_result(self, result):
    print "The result is... "

    print self[result]

def comms(arg):
    from twisted.internet.protocol import Protocol, Factory
    from twisted.internet import reactor
    from twisted.internet.defer import Deferred

    import cloudProtocol

    d = Deferred()

    reactor.connectTCP("127.0.0.1",64000, cloudProtocol.CloudClientFactory(d))

    return d

def transmit_message(self):
    print self

if __name__ == '__main__':


  # create a node object
  app_node = ApplicationNode()
  #app_node.run()

  from twisted.internet import reactor

  # launch the interactive mode
  stdio.StandardIO(UserInputBot(app_node))

  reactor.run()
