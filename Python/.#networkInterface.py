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
        
        # HERE--> Implementation specific node instanciation
        from kademlia.network import Server()
        self._node = Server()
        # END OF SECTION 


        
    def connect(self, port):
        
        if(self._app_deployer):
            from twisted.application import service, internet
            from twisted.python.log import ILogObserver
            from twisted.internet import reactor, task

            import sys, os
            sys.path.append(os.path.dirname(__file__))
            from kademlia.network import Server
            from kademlia import log

            application = service.Application("kademlia")
            application.setComponent(ILogObserver, log.FileLogObserver(sys.stdout, log.INFO).emit)

            if os.path.isfile('cache.pickle'):
                kserver = Server.loadState('cache.pickle')
            else:
                kserver = Server()
                kserver.bootstrap([("127.0.0.1", port)])
                kserver.saveStateRegularly('cache.pickle', 10)
                
            server = internet.UDPServer(8468, kserver.protocol)
            server.setServiceParent(application)    
        
        
    def connect(self, port):
        
        if(self._app_deployer):
            from twisted.application import service, internet
            from twisted.python.log import ILogObserver
            from twisted.internet import reactor, task

            import sys, os
            sys.path.append(os.path.dirname(__file__))
            from kademlia.network import Server
            from kademlia import log

            application = service.Application("kademlia")
            application.setComponent(ILogObserver, log.FileLogObserver(sys.stdout, log.INFO).emit)

            if os.path.isfile('cache.pickle'):
                kserver = Server.loadState('cache.pickle')
            else:
                kserver = Server()
                kserver.bootstrap([("127.0.0.1", port)])
                kserver.saveStateRegularly('cache.pickle', 10)
                
            server = internet.UDPServer(8468, kserver.protocol)
            server.setServiceParent(application)    
        
        
    def connect(self, port):
        
        if(self._app_deployer):
            from twisted.application import service, internet
            from twisted.python.log import ILogObserver
            from twisted.internet import reactor, task

            import sys, os
            sys.path.append(os.path.dirname(__file__))
            from kademlia.network import Server
            from kademlia import log

            application = service.Application("kademlia")
            application.setComponent(ILogObserver, log.FileLogObserver(sys.stdout, log.INFO).emit)

            if os.path.isfile('cache.pickle'):
                kserver = Server.loadState('cache.pickle')
            else:
                kserver = Server()
                kserver.bootstrap([("127.0.0.1", port)])
                kserver.saveStateRegularly('cache.pickle', 10)
                
            server = internet.UDPServer(8468, kserver.protocol)
            server.setServiceParent(application)    
        
        
    def connect(self, port):
        
        if(self._app_deployer):
            from twisted.application import service, internet
            from twisted.python.log import ILogObserver
            from twisted.internet import reactor, task

            import sys, os
            sys.path.append(os.path.dirname(__file__))
            from kademlia.network import Server
            from kademlia import log

            application = service.Application("kademlia")
            application.setComponent(ILogObserver, log.FileLogObserver(sys.stdout, log.INFO).emit)

            if os.path.isfile('cache.pickle'):
                kserver = Server.loadState('cache.pickle')
            else:
                kserver = Server()
                kserver.bootstrap([("127.0.0.1", port)])
                kserver.saveStateRegularly('cache.pickle', 10)
                
            server = internet.UDPServer(8468, kserver.protocol)
            server.setServiceParent(application)    
        
        
    def connect(self, port):
        
        if(self._app_deployer):
            from twisted.application import service, internet
            from twisted.python.log import ILogObserver
            from twisted.internet import reactor, task

            import sys, os
            sys.path.append(os.path.dirname(__file__))
            from kademlia.network import Server
            from kademlia import log

            application = service.Application("kademlia")
            application.setComponent(ILogObserver, log.FileLogObserver(sys.stdout, log.INFO).emit)

            if os.path.isfile('cache.pickle'):
                kserver = Server.loadState('cache.pickle')
            else:
                kserver = Server()
                kserver.bootstrap([("127.0.0.1", port)])
                kserver.saveStateRegularly('cache.pickle', 10)
                
            server = internet.UDPServer(8468, kserver.protocol)
            server.setServiceParent(application)    
        
        
    def connect(self, port):
        
        if(self._app_deployer):
            from twisted.application import service, internet
            from twisted.python.log import ILogObserver
            from twisted.internet import reactor, task

            import sys, os
            sys.path.append(os.path.dirname(__file__))
            from kademlia.network import Server
            from kademlia import log

            application = service.Application("kademlia")
            application.setComponent(ILogObserver, log.FileLogObserver(sys.stdout, log.INFO).emit)

            if os.path.isfile('cache.pickle'):
                kserver = Server.loadState('cache.pickle')
            else:
                kserver = Server()
                kserver.bootstrap([("127.0.0.1", port)])
                kserver.saveStateRegularly('cache.pickle', 10)
                
            server = internet.UDPServer(8468, kserver.protocol)
            server.setServiceParent(application)    
        
        
    def connect(self, port):
        
        if(self._app_deployer):
            from twisted.application import service, internet
            from twisted.python.log import ILogObserver
            from twisted.internet import reactor, task

            import sys, os
            sys.path.append(os.path.dirname(__file__))
            from kademlia.network import Server
            from kademlia import log

            application = service.Application("kademlia")
            application.setComponent(ILogObserver, log.FileLogObserver(sys.stdout, log.INFO).emit)

            if os.path.isfile('cache.pickle'):
                kserver = Server.loadState('cache.pickle')
            else:
                kserver = Server()
                kserver.bootstrap([("127.0.0.1", port)])
                kserver.saveStateRegularly('cache.pickle', 10)
                
            server = internet.UDPServer(8468, kserver.protocol)
            server.setServiceParent(application)    
        
        
    def connect(self, port):
        
        if(self._app_deployer):
            from twisted.application import service, internet
            from twisted.python.log import ILogObserver
            from twisted.internet import reactor, task

            import sys, os
            sys.path.append(os.path.dirname(__file__))
            from kademlia.network import Server
            from kademlia import log

            application = service.Application("kademlia")
            application.setComponent(ILogObserver, log.FileLogObserver(sys.stdout, log.INFO).emit)

            if os.path.isfile('cache.pickle'):
                kserver = Server.loadState('cache.pickle')
            else:
                kserver = Server()
                kserver.bootstrap([("127.0.0.1", port)])
                kserver.saveStateRegularly('cache.pickle', 10)
                
            server = internet.UDPServer(8468, kserver.protocol)
            server.setServiceParent(application)    
    
    def bootStrapDone(self, server):
        print self
        print server
        contacts = self.inetVisibleIP()
        print contacts

        
    def connect(self, port):
        
        if(self._app_deployer):
            from twisted.application import service, internet
            from twisted.python.log import ILogObserver
            from twisted.internet import reactor, task

            import sys, os
            sys.path.append(os.path.dirname(__file__))
            from kademlia.network import Server
            from kademlia import log

            application = service.Application("kademlia")
            application.setComponent(ILogObserver, log.FileLogObserver(sys.stdout, log.INFO).emit)

            if os.path.isfile('cache.pickle'):
                kserver = Server.loadState('cache.pickle')
            else:
                kserver = Server()
                kserver.bootstrap([("127.0.0.1", port)])
                kserver.saveStateRegularly('cache.pickle', 10)
                
            server = internet.UDPServer(8468, kserver.protocol)
            server.setServiceParent(application)    
        else:
            self._node.listen(port)
            self._node.bootstrap([("127.0.0.1",port)]).addCallback(self.bootStrapDone)
