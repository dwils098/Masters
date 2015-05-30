from twisted.internet import defer, threads
from twisted.internet.defer import Deferred, DeferredQueue
from twisted.python import log
          
################################################################################
#                          Web USER RELATED CODE                               #
################################################################################

"""
Very simple web server using cherrypy

Simply spin a CherryPy webServer on a subprocess
"""
def simple_web(args):
    # use the existing database...
    import os
    import signal
    from subprocess import Popen, PIPE
    pipe_rfd, pipe_wfd = os.pipe()
    rfd, wfd = os.pipe()
    
    print(pipe_rfd, pipe_wfd)
    
    app = args[0]
    webServer_string = args[0]._webServer_module
    # The os.setsid() is passed in the argument preexec_fn so
    # it's run after the fork() and before  exec() to run the shell.
    app._web = Popen(['python','-u', webServer_string], stdin=rfd, stdout=pipe_wfd, close_fds=False)
    app._web_PIPE_Inc = pipe_rfd
    app._web_PIPE_Out = wfd
    app._web_REPLY = 0
    
    
################################################################################
#                        Worker USER RELATED CODE                              #
################################################################################

"""
Example function that contains application logic and is created as an compositional
part of a task.

First parameter refers to the Task object.

Second parameter refers to a list of arguments.

"""
def ex_function(task_obj, param_2):

  result = param_2[0] * param_2[1]

  print task_obj.creator

  task_obj.d.addCallback(print_result)
  
  task_obj.results = result

  return result

def print_result(result):
  print "Result is :", result


# Helping function that simply fire the deferred of a task object.
def task_func (task_obj):
  # simply execute the deferred
  task_obj.d.callback(task_obj)


class Task (object):
    """
    This object represent a task in our system and it is an abstraction of an actual task.
    """
    # Task Types
    Web = 0
    Worker = 1
    Data = 2
    Undefined = 3

    def __init__(self, creator):
      # use UUID as defined in RFC 4122
      import uuid
      self.uuid = str(uuid.uuid1()) 
      self.type = Task.Undefined
      self.creator = creator
      self.completed = False
      self.results = 0
      self.d = Deferred()
    
    def __str__(self):
        return 'Task: [uuid = '+ str(self.uuid) + ' ] [creator = ' + self.creator + ' ] [type = ' + str(self.type) + ']'
        
    def __eq__(self,other):
      return self.uuid == other.uuid

    def __ne__(self,other):
      return not self.__eq__(other)

    def create(self, package,func, args):
      # simply add a deferred
      print 'in CREATE'
      import importlib
      module_to_call = importlib.import_module(package)
      method_to_call = getattr(module_to_call, func)
      self.d.addCallback(method_to_call,args)


class ApplicationNode (object): 
    """
    This class represents an ApplicationNode which is a node that is contributing to the
    application, AND NOT A APPLICATION DEPLOYER. It is updated from the deprecated ApplicationNode.py
    to use the network implementation interface.
    """

    def __init__(self, aD, webApplication_module, webServer_module):
        
        # any attributes ...
        if aD == 'True':
            self._appDeployer = True
            
            # queues to contain the jobs to be completed
            self._queues = [DeferredQueue()] * 3
            self._pending = [[]] * 3

            # web process pointer
            self._web = ""

        else:
            self._appDeployer = False
            self._type = Task.Undefined
        
        self._webApplication_module = webApplication_module
        self._webServer_module = webServer_module

        # Logic to instantiate using the network implementation interface
        from networkInterface import NetworkInterface
        self._netHandle = NetworkInterface()
      
    # ---- TASK RELATED FUNCTIONS ---- #
    def addTask (self, task):
        # simply add the task to the corresponding queue
        self._queues[task.type].put(task)

    def addPendingTask (self, task):
        self._pending[task.type].append(task)

    def getTask (self, task_type):
        # simply return the top elt of the queue
        # and add a callback to fire it's deferred
        return self._queues[task_type].get()

        
    def getPendingTask(self, task):
      # verify that this is a task that was offloaded 
      if task in self._pending[task.type]:
        # indicate that it is complete
        task.completed = True
        # remove task from pending
        self._pending[task.type].remove(task)
      return task

    
    # ---- END OF TASK FUNCTIONS  ---- #
    
    # used to call repeatedly to retrieve on livee nodes...        
    def retryContact(self, contactable_nodes):
        # call slow function...
        while contactable_nodes is []:
            contactable_nodes  = self._netHandle.retrieveContacts()
            import time 
            time.sleep(4)
            
    # will need to call the resource advertizement process upon completion
    def onProcessDone(self, result):
        
        def handle_results(self,node):
          
          def getRequest(node):
            
            node._netHandle._log.debug('Getting request...')
            print 'response from child process : ',node._web.stdout.readline()
            
          def gotRequests(res, node):
            

            
            from twisted.internet import stdio
            import importlib
            
            webProtocol_x = importlib.import_module(node._webApplication_module)



            res = stdio.StandardIO(webProtocol_x.WebProtocol(node), 
                                   stdin=node._web_PIPE_Inc, 
                                   stdout=node._web_PIPE_Out)
            node._netHandle._log.info("In GOT REQUEST --> " + str(res))
            
          print "in handle:", self
          
          if node._appDeployer :
            #start web server...
            node._netHandle._log.info('Starting Web Server...')
            
            thread = threads.deferToThread(simple_web, [node])
            thread.addCallback(gotRequests, node)

            

        def bind(results, ip, self):
            print "reday to bind it!"
            print  results, self
            from twisted.internet.protocol import Protocol, Factory
            from twisted.internet import reactor
            from twisted.internet.defer import Deferred
            import cloudProtocol
            d = Deferred()
            
            factory = cloudProtocol.CloudClientFactory(d,self)
            factory.protocol = cloudProtocol.CloudComms
            factory.clients = []
             
            # if an application deployer simply listen on the port no need for ip (arg)
            if self._appDeployer:
                reactor.listenTCP(64000, factory)
                print  "listening on port 64000..."
            # if not, then connect to the node that selected you
            else:    
                reactor.connectTCP('192.168.56.1', 64000, factory)
                print "connected to 192.168.56.1  @ ", 64000 
            print "Cloud Comms server started"
        
            #factory.protocol.message(factory.protocol,"Server's MEssage!")
            if not reactor.running:
                reactor.run()
        

        if self._appDeployer:
            
            self._netHandle._log.debug('Seeking mechanism...')
            #this node is seeking resources...
            import resAdvProtocol as rAP
            # blocking operation, thus push to separate thread
            from twisted.internet import threads
            
            # H-C Value --> known_node = 192.168.56.101
            thread = threads.deferToThread(rAP.seek_resources, ['192.168.56.101','127.0.0.1'])
            thread.addCallback(handle_results, self)
            
        else:
            self._netHandle._log.debug('Advertising mechanism...')
            #this node is seeking resources...
            import resAdvProtocol as rAP
            # blocking operation, thus push to separate thread
            from twisted.internet import threads
            thread = threads.deferToThread(rAP.advertize, self.ip)
            thread.addCallback(handle_results,self)
            
        # once the selection phase is over, begin the binding phase
        thread.addCallback(bind, self.ip, self)
    
    # after connection complete...
    def _waitForOtherNodes(self, results):
        from twisted.internet import threads
        
        # attempt to retrieve a list of contactable nodes
        contactable_nodes = self._netHandle.retrieveContacts()
        
        # if our initial attempt does not reveal any nodes, simply defer to thread.
        if contactable_nodes == []:
            deferred = threads.deferToThread(self.retryContact, contactable_nodes)
            deferred.addCallback(self.onProcessDone)
    
    def run(self,ip,port):

        self.ip = ip
        self.port = int(port)
        # connect to the network
        deferred = self._netHandle.connect(self.port,5556,self.ip)
        
        # addCallbacks to this deferred to execute functions upon completion of connection
        deferred.addCallback(self._waitForOtherNodes)
        
        from twisted.internet import reactor
        
        reactor.run()

if __name__ == '__main__':
    import sys

    print sys.argv
    
    node =  ApplicationNode(sys.argv[3])
    
    from twisted.python import log
    log.startLogging(sys.stdout)
    
    node.run(sys.argv[1], sys.argv[2])
