from entangled.kademlia import node
from twisted.internet.defer import Deferred
import networkserviceapi

def node_hello_world(self):
    # This function simply schedule a task: print_contacts function,
    # it needs to be executed after a short delay to allow joinNetwork
    # cycles to finish, here the delay is set to: 0.01 seconds.

    from twisted.internet import reactor, task
    d = task.deferLater(reactor,0.01, print_contacts, self)
    return d


def find_it(self,node, key):
    # wrapping function to find a key in the DHT, and proceed to print the associated value.

    result = node.iterativeFindValue(key)
    result.addCallback(print_it, key)

    return result

def store_it(self,node, service):
    # wrapping function to find a key in the DHT, and proceed to print the associated value.
    print "store_it"

    result = networkserviceapi.postService(node, service)

    return result

def find_service (self, node ,service):
    # wrapping function to find a key in the DHT, and proceed to print the associated value.
    from twisted.internet import reactor, task
    d = task.deferLater(reactor, 1, networkserviceapi.findService, node,service)

    d.addCallback(print_service, "Robin Williams")

    print "find_service ", d
    return d

def error_joining(self):
    print "Error"

def print_contacts(self):
    for i in range (len(self)):
        print "Node[",i,"]: "
        self[i].printContacts()

def print_service(self,name):
    print "in print_service"
    import pickle

    #de-serialize the value retrieved.

    service = pickle.loads(self[name])

    print "Value for Service name : ", name, " is ", service

def print_it(self,key):
    print "Value for key : ", key, " is ", self[key]

def initialize_net(num_nodes):
    # This function initialize a local host network with Kademlia nodes
    nodes = []
    d = Deferred()

    # Make them join the net...
    for i in range(0, num_nodes):
        nodes.append(node.Node(4020+int(i)))
        print "Node: ", i, "joined the Network."



    knownNodes = [("127.0.0.1", 4020)]
    for i in range (0, num_nodes):
        nodes[i].joinNetwork(knownNodes)

    # insert one dummy value just to test the DHT
    nodes[0].iterativeStore("a_key","a_value")

    d.callback(nodes)
    print "End of initialize_net"

    return d, nodes

def main():
    from twisted.internet import reactor
    d, nodes = initialize_net(5)
    d.addCallbacks(node_hello_world, error_joining)
    d.addCallback(find_it, nodes[1],"a_key")
    service = networkserviceapi.Service("Robin Williams")
    d.addCallback(store_it, nodes[2], service)
    d.addCallback(find_service, nodes[3], "Robin Williams")



    reactor.run()


if __name__ == '__main__':
    main()
