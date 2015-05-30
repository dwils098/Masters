from twisted.python import log
from twisted.internet.defer import Deferred
from kademlia.log import Logger

"""
This Interface will serve as a implementation independent layer to separate the implementation
independent instruction from the Cloud Infrastructure. It will wrap the functionalities and provide 
a unified way to access them.
"""

class NetworkInterface (object):

    # Create a NetworkInterface object to accomplish all network related tasks
    def __init__(self, appDeployer, uuid):
        self._connected = False
        self._app_deployer = appDeployer

        # optional...
        self._number_of_nodes = 0
        self._list_of_nodes =[] 
        
        # logging capabilities
        self._log = Logger(system=self)

        # HERE--> Implementation specific node instanciation
        from kademlia.network import Server
        import kademlia
        import os
        path = os.path.dirname(kademlia.__file__)
        print "PATH TO KADEMLIA: --> ", path
        self._node = Server()
        self._node.log.level = 4
        # END OF SECTION 


    def bootStrapDone(self, results, node, ip_toPort_tuple):
        
        if len(results) == 0:
            print "Well that's embarassing, no one responded."
            # could not contact nodes simply retry until able to ...
            return self.bootStrap(node, ip_toPort_tuple)


    def bootStrap(self, node, ip_toPort_tuple):
        print "Bootstrapping..."
        #contacts = self._node.inetVisibleIP()
        deferred = Deferred()

        deferred= node.bootstrap(ip_toPort_tuple)

        deferred.addCallback(self.bootStrapDone, node, ip_toPort_tuple )
        return deferred
        
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

        deferred = Deferred()
        #print "in connect ... "  
        #print "now listening on port: ",fromPort
        self._node.listen(fromPort)

        deferred = self.bootStrap( self._node, [(ip,toPort), ('192.168.56.103',toPort)])

        return deferred

# self._node.boostrap([(ip,toPort)]).addCallback(self.bootStrapDone, self._node, ip, toPort)

            
    # This function is used to set a value in the DHT
    def setDone(self,result):
        print result
        print "set is done"
        deferred = Deferred()
        return deferred

    def set(self, key, value):

        def _processKey(result, key, values):
            print result, key, values
            deferred = Deferred()
            # upon recovering the value of the key
            if result == None:
                deferred = self._node.set(key, values)
                return deferred 
                #.addCallback(self.setDone)
            else:
                for value in values:
                    if value not in result: 
                        # append + publish
                        result.append(value)
                    else:
                        self._log.info("Value is already in the corresponding key.")
                deferred = self._node.set(key, result)
            return deferred
            

        # Only application deployers are allowed to write to the DHT.
        if self._app_deployer != False: 
            deferred = Deferred()           
            # Two possible keys are allowed to be written to, the template key and their respective application key
            if ('template' == key or self._uuid == key) and key != None:
                # HERE --> Implementation Specific Code
                print  " :::  ", self,  " ::: ", key, " ::: ", value, " <----------------------------" 
                # if writing to the template, retrieve the value first then append to it if necessary
                if key == 'template':

                    deferred = self._node.get(key)
                    deferred.addCallback(_processKey, key, value)
                    return deferred
                    #self._node.set(key, value).addCallback(self.setDone)
                # END OF SECTION

        # Not Allowed to write to the DHT.
        else:
            self._log.info("Only application deployers are allowed to write values into the DHT!")
            

    def done(self,result):
        print "self: ", self
        print "Key result:", result

    def get(self,result, key):
        # HERE --> Implementation Specific Code
        print result, " :::  ", self,  " ::: ", key, " <----------------------------" 
        deferred = self._node.get(key)
        deferred.addCallback(self.done)
        return deferred
        # END OF SECTION
