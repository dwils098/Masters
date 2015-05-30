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
    
    app._web = Popen(['python','-u', webServer_string],bufsize=-1,stdin=rfd, stdout=pipe_wfd, close_fds=False)
    
    
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
      # include module name and func name to callback in new job...
      self.job_callback =[]
      self.d = Deferred()
      
      # used when dealing with very large data
      self._job_data = False
    
    def __str__(self):
        return 'Task: [uuid = '+ str(self.uuid) + ' ] [creator = ' + self.creator + ' ] [type = ' + str(self.type) + ']'
        
    def __eq__(self,other):
      return self.uuid == other.uuid

    def __ne__(self,other):
      return not self.__eq__(other)

    def create(self, package,func, args):
      # simply add a deferred
      import importlib, inspect
      
      module_to_call = importlib.import_module(package)
      method_to_call = "not_set"
      class_list = inspect.getmembers(module_to_call, inspect.isclass)
      if class_list is not []:
          # identify a class containing the proper func...
          print class_list
          for class_tuple in class_list:
              
              cand_class = class_tuple[1]
              if hasattr(cand_class, func):
                  method_to_call = getattr(cand_class, func)
              
      
      # couldn't find the function in the classes, let's simply look in the module.
      if method_to_call == "not_set":
          method_to_call = getattr(module_to_call, func)
      print "Task:CREATE=> Method: ",method_to_call
      
      
      
      self.d.addCallback(method_to_call, args)

class ApplicationNode (object): 
    """
    This class represents an ApplicationNode which is a node that is contributing to the
    application, AND NOT A APPLICATION DEPLOYER. It is updated from the deprecated ApplicationNode.py
    to use the network implementation interface.
    """

    def __init__(self, aD, webApplication_module, webServer_module):
        
        # any attributes ...
        if aD == 'True':
            
            # unique identifier, representing application in the network.
            import uuid
            self._uuid = str(uuid.uuid1())
            
            self._appDeployer = True
            
            # queues to contain the jobs to be completed
            #self._queues = [DeferredQueue()] * 3
            # need to replace conflicting when in a array!
            self._w_queue = DeferredQueue()
            self._d_queue = DeferredQueue()
            self._w_job_count = 0
            self._d_job_count = 0
            self._pending = [[]] * 3

            # web process pointer
            self._web = ""

            # dbHandle pointer set to false if node is not a DB_ROLE.
            self._dbHandle = False

        else:
            self._appDeployer = False
            self._uuid = None
            self._type = Task.Undefined
            self._dbHandle = False
        

        self._webApplication_module = webApplication_module
        self._webServer_module = webServer_module

        # Logic to instantiate using the network implementation interface
        from networkInterface import NetworkInterface
        # pass the uniqueID 
        self._netHandle = NetworkInterface(self._appDeployer,self._uuid)
      
    # ---- TASK RELATED FUNCTIONS ---- #
    def addTask (self, task):
        # simply add the task to the corresponding queue
        #print 'Adding task to queue: ' + task.type
        if task.type == Task.Worker:
            self._w_queue.put(task)
            self._w_job_count += 1
        elif task.type == Task.Data:
            self._d_queue.put(task)
            self._d_job_count += 1
        else: 
            print 'This task does not correspond to any acceptable types...'

    def addPendingTask (self, task):
        self._pending[int(task.type)].append(task)

    def getTask (self, task_type):
        # simply return the top elt of the queue
        # and add a callback to fire it's deferred
        if task_type == Task.Worker:
            deferred = self._w_queue.get()
            self._w_job_count -= 1
            return deferred
        elif task_type ==  Task.Data:
            deferred = self._d_queue.get()
            self._d_job_count -= 1
            return deferred
        else:
            print 'This task does not correspond to any acceptable types...'

        
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
        self._netHandle._log.debug('RetryContact...')
        # call slow function...
        while contactable_nodes is []:
            contactable_nodes  = self._netHandle.retrieveContacts()
            import time 
            time.sleep(4)
    
        for nodes in contactable_nodes:
            self._netHandle._log.debug("Contactable-Nodes: "+nodes)
            
    # will need to call the resource advertizement process upon completion
    def onProcessDone(self, result):
        
        def handle_results(self,node):
            
          def gotRequests(res, node):
            
            from twisted.internet import stdio
            import importlib
            node._netHandle._log.debug(node._webApplication_module)
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
            #factory.protocol = cloudProtocol.CloudComms
            #factory.clients = []
             
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
        # --------------------------------------------------------------------------------
        neighbors =[]
        while len(neighbors) < 2:
            neighbors = self._netHandle._node.protocol.router.findNeighbors(self._netHandle._node.node, k=10)
            print "Neighbors.."
            print neighbors 
            
            import time 
            time.sleep(3)

        ip_list = []

        for n in neighbors:
            print "Node: " + str(n.ip)
            ip_list.append(n.ip)
        #--------------------------------------------------------------------------------

        #executing thread...
        thread = Deferred()

        if self._appDeployer:
            def _seek(res,self):
                self._netHandle._log.debug('Seeking mechanism...')
                
                #this node is seeking resources...
                import resAdvProtocol as rAP
                # blocking operation, thus push to separate thread
                from twisted.internet import threads
            
                # H-C Value --> known_node = 192.168.56.101
                thread = threads.deferToThread(rAP.seek_resources, ip_list)
                thread.addCallback(handle_results, self)
                thread.addCallback(bind, self.ip, self)

            attributes = []
            # first publish the RS template from the configuration file...
            with open('config.cfg', 'r') as config_file:
                for entry in config_file: 
                    entry=entry.strip('\n')
                    if "db_nodes" in entry:
                        tag, num = entry.split()
                        self._db_nodes_num = num
                    attributes.append(entry)
            
            self._netHandle.set('template', str(attributes)).addCallback(_seek, self)

            
        else:
            
            def _advertise(template,self):
                
                self._netHandle._log.debug('Advertising mechanism...')
                self._netHandle._log.debug('Template: '+str(template))

                #this node is seeking resources...
                import resAdvProtocol as rAP
                # blocking operation, thus push to separate thread
                from twisted.internet import threads
                thread = threads.deferToThread(rAP.advertize, self.ip)
                thread.addCallback(handle_results,self)
                thread.addCallback(bind, self.ip, self)

            # first retrieve the RS template, pass it to the advertising mechanism.
            self._netHandle.get('','template').addCallback(_advertise,self)

        # once the selection phase is over, begin the binding phase
        #thread.addCallback(bind, self.ip, self)
    
    # after connection complete...
    def _waitForOtherNodes(self, results):
        from twisted.internet import threads
       #B
       #eployer:
       #
       #("JAMES")
       #ask.Data
       #
       #ask(db)
       #
        self._netHandle._log.debug('_waiting for other nodes...')
        # attempt to retrieve a list of contactable nodes
        contactable_nodes = self._netHandle.retrieveContacts()
        
        # if our initial attempt does not reveal any nodes, simply defer to thread.
        if contactable_nodes == []:
            deferred = threads.deferToThread(self.retryContact, contactable_nodes)
            deferred.addCallback(self.onProcessDone)
        else:
            self.onProcessDone(contactable_nodes)
            
    def run(self,ip,port,iitn):

        self.ip = ip
        self.port = int(port)
        self.iitn= iitn

        ip_in_the_network = iitn

        # connect to the network
        deferred = self._netHandle.connect(self.port,5555,ip_in_the_network)
        
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
    
    node.run(sys.argv[1], sys.argv[2], sys.argv[4])
