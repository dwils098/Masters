from twisted.python import log
from kademlia.log import Logger

"""
This Interface will serve as a implementation independent layer to separate the implementation
independent instruction from the Cloud Infrastructure. It will wrap the functionalities and provide 
a unified way to access them.
"""

class NetworkInterface (object):

    # Create a NetworkInterface object to accomplish all network related tasks
    def __init__(self, appDeployer=False):
        self._connected = False
        self._app_deployer = appDeployer

        # optional...
        self._number_of_nodes = 0
        self._list_of_nodes =[] 
        
        # logging capabilities
        self._log = Logger(system=self)

        # HERE--> Implementation specific node instanciation
        from kademlia.network import Server
        self._node = Server()
        self._node.log.level = 4
        # END OF SECTION 

    def bootStrapDone(self, server):
        #contacts = self._node.inetVisibleIP()
        print "BOOOOTTTT STAPPP IT"

    def retrieveContacts(self):
        """
        NEED TO FIND A WAY TO RETRIEVE THE LIST OF NEIGHBORS !!!
        
        """
        # !!! DOES EXACTLY THE SAME AS bootstrappableNeighbors !!!
        for bucket in self._node.protocol.router.buckets:
            print bucket.getNodes()
        
        # !!! bootstrappableNeighbors returns only the list of neighbors that you provided as !!!
        # !!! a bootstrap list, that are also online !!!
        neighbors =  self._node.bootstrappableNeighbors()
        
        print neighbors
        return neighbors

    def connect(self,fromPort,toPort,ip='127.0.0.1'):
        self._log.debug('Connecting...')
        #print "in connect ... "  
        #print "now listening on port: ",fromPort
        self._node.listen(fromPort)
        return self._node.bootstrap([(ip,toPort)]).addCallback(self.bootStrapDone)
            
    # This function is used to set a value in the DHT
    def setDone(self,result):
        print result
        print "set is done"
        
    def set(self,result, key, value):
        # HERE --> Implementation Specific Code
        print result, " :::  ", self,  " ::: ", key, " ::: ", value, " <----------------------------" 
        self._node.set(key, value).addCallback(self.setDone)
        # END OF SECTION

    def done(self,result):
        print "self: ", self
        print "Key result:", result

    def get(self,result, key):
        # HERE --> Implementation Specific Code
        print result, " :::  ", self,  " ::: ", key, " <----------------------------" 
        self._node.get(key).addCallback(self.done)

        # END OF SECTION
