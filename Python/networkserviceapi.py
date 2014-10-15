from entangled.kademlia import node
from twisted.internet import defer

import hashlib, random, time

class Service (object):
    # This class represent a service object.

    def __init__ (self, name="service_default", description="description_default", provider_ip="0.0.0.0", provider_port=4000):
        self.name = name
        self.description = description
        self.provider_ip = provider_ip
        self.provider_port = provider_port
        self.id = self._generateID(self.name)

    def __str__(self):
        return "Service: [name] = " + self.name + " [description] = " + self.description + " [provider_ip] = " + self.provider_ip + " [provider_port] = " + str(self.provider_port)

    def _generateID(self, string):
        """ Generates a 160-bit pseudo-random identifier from the object string representation

        @return: A globally unique 160-bit pseudo-random identifier
        @rtype: str
        """
        hash = hashlib.sha1()
        hash.update(str(string))
        print "ID : ", string
        return hash.digest()

def print_result(self, service_name):
    print "The result is... "

    # unserialize the result...
    import pickle

    service = pickle.loads(self[service_name])


    print service

def findService (calling_node, service_name):
    """
    Description: A node looks for a given service using this method and
    retrieves the location of the service provider using the overlay network.

    Inputs:
      calling_node: node calling this function.
      service_name: name of the service to find.

    Returns: The Service object representing that service (which contains the IP
    of the provider, and the port on which it is advertized).
    """
    #print "findService: ", service_name

    result = calling_node.iterativeFindValue(service_name)

    result.addCallback(print_result, service_name)

    return result


def postService (node, service):
    """
    Description: A node post a given service to indicate to the other
    DHT nodes that they provide this service.

    Inputs: name of the service to find.

    Returns: Location of the service (Ip_address), and *null* if service doesn't exist.
    """
    print "postService: ", service.name

    # serialize the Service obj using Pickle
    import pickle
    service_pickled = pickle.dumps(service)
    service_as_a_str = str(service_pickled)

    # simply store the value in the DHT
    result = node.iterativeStore(service.name,service_as_a_str)

    return result



def requestService (service_name):
    print "requestService: ", service_name
