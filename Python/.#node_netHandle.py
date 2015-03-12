from twisted.internet import defer
from twisted.internet.defer import Deferred

class ApplicationNode (object): 
    """
    This class represents an ApplicationNode which is a node that is contributing to the
    application, AND NOT A APPLICATION DEPLOYER. It is updated from the deprecated ApplicationNode.py
    to use the network implementation interface.
    """

    def __init__(self):
        
        # any attributes ...

        # Logic to instantiate using the network implementation interface
        from networkInterface import NetworkInterface
        self._netHandle = NetworkInterface()
        
    """
    This represent an idle event, that reschedules itself, to add a callback to.
    """
    @defer.inlineCallbacks
    def _idle(self, res):
        # deferred to make it reschedule itself
        d = Deferred()
        
        # verify if there are other nodes in the network
        # if not simply reschedule... because until there is at least two nodes in the
        # network, well dabbing in the domain of obviousness, it is not a network.
        contact_list =  self._netHandle.retrieveContacts()
        # FOR DEBUGGING PURPOSES GENERATE A LIST AFTER
        #contact_list = []
        print res, self
        if contact_list == []:
            print "in idle"
            import time
            time.sleep(2)
            print res, self, contact_list
            res = yield self._idle(res)
        # if so return a deferred to which we can attach a callback (to be called)
        print res
    
    # used to call repeatedly to retrieve on line nodes...        
    def processFunction(self, processArgument):
        # call slow function...
        while processArgument is []:
            processArgument = self._netHandle.retrieveContacts()
            import time 
            time.sleep(4)
            print processArgument
            
    # will need to call the resource advertizement process upon completion
    def onProcessDone(self, result):
        
        def handle_results(self):
            print result
        
        
        import sys 

        if sys.argv[2] == 'True':
            print "SEEEEKE ITT!"
            #this node is seeking resources...
            import resAdvProtocol as rAP
            # blocking operation, thus push to separate thread
            from twisted.internet import threads
            thread = threads.deferToThread(rAP.seek_resources, result)
            thread.addCallback(handle_results)
        else:
            print "ADVERTIZE IT!!!"
            #this node is seeking resources...
            import resAdvProtocol as rAP
            # blocking operation, thus push to separate thread
            from twisted.internet import threads
            thread = threads.deferToThread(rAP.advertize)
            thread.addCallback(handle_results)

    # after connection complete...
    def _waitForOtherNodes(self, results):
        from twisted.internet import threads
        
        contactable_nodes = self._netHandle.retrieveContacts()
        
        # if our initial attempt does not reveal any nodes, simply defer to thread.
        if contactable_nodes == []:
            deferred = threads.deferToThread(self.processFunction, contactable_nodes)
            deferred.addCallback(self.onProcessDone)
    
    def run(self,port):
        
        port = int(port)
        # connect to the network
        deferred = self._netHandle.connect(port,5556)
        
        # addCallbacks to this deferred to execute functions upon completion of connection
        deferred.addCallback(self._waitForOtherNodes)
        
        
        

        from twisted.internet import reactor
        
        reactor.run()

if __name__ == '__main__':
    import sys

    print sys.argv
    node =  ApplicationNode()
    
    node.run(sys.argv[1])
