from twisted.internet.protocol import Protocol, Factory, ClientFactory
from twisted.internet import reactor
from node_netHandle import Task
from twisted.internet.defer import inlineCallbacks

"""
We have defined the following protocol for interactions between nodes 
within the Cloud infrastructure:
   (0) Connect via TCP. 
   (0.1) [not implemented yet] Authentication.
   (1) [Deployer] Indicate what type of node [Node] will be.
   (2) [Node] Request Job.
       [Deployer] Reply with Job if any pending, else reply with idle job.
   (3) [Node] Return Results from Job.
       [Deployer] Consume Results.
   (4) Repeat (2) and (3) until [Node] receives Last_Job. 
"""

class CloudComms(Protocol):
    appD = 0
    log = 0
    node = 0

    def connectionMade(self):
        self.message('connected')
        self.factory.clients.append(self)
        print "clients are ", self.factory.clients
        self.ctr = 0

        global appD, log,node
        appD = self.factory.node._appDeployer
        log = self.factory.node._netHandle._log
        node = self.factory.node

    def connectionLost(self, reason):
        #self.factory.clients.remove(self)
        print 'Lost connection.  Reason:', reason

    def dataReceived(self, data):

        print("Receiving Data from %s" % self.transport.getPeer())

        # [Deployer] Negotiate with node what role they will accomplish.
        if('connected' in data):
            # connection is complete...
            # (1) of protocol
            if appD:
                self.negotiateType()
            elif not appD:
                pass
            else:
                log.error("Cannot identify whether it is an application deploying node or not")
            #self.message("ping")
            #self.message(self.factory.node._secretVal)
        
        # [Node] A role was assigned to you, now request a job.
        if('WORKER' in data):
            if not appD:
                # ok, set type then request job
                self.factory.node._type = Task.Worker
                self.node_jobRequest()
                
            elif appD:
                log.error("Something's wrong this was not meant for you!")
        
        # [Node] Received a dispatch notice, thus a job is available, request it! 
        if('DISPATCH' in data):
            if not appD:
                # all queues are empty
                if 'none' in data:
                    # wait 1 second and retry 
                    import time 
                    time.sleep(1)
                    log.info('AppD has no jobs, ack it!')
                    self.transport.write('BACK')
                # job available    
                else:    
                    log.info('DISPATCH -- > REQUEST JOB!')
                    self.node_jobRequest()
            else:
                log.error("Really this transporter is really confused...")
        
        # [Deployer] Dispatch bounced back retry...
        if('BACK' in data):
            if appD:
                log.info('Recv. BACK')
                self.deployer_dispatch()
            else:
                log.error('The force is strong with you, young padawan, but only a true Jedi can perform this!')

        # [Deployer] A job was requested of a specific type
        if ('TYPE' in data):
            tag, job_type = data.split()
            job_type = int(job_type)
            self.deployer_jobReply(job_type)
            
        
        # [Node] A job was received, separate Tag from pickle data dump...
        if ('JOB' in data):
            tag, job = data.split(' --.-- ')
            self.node_jobReceived(job)
            
        # [Deployer] A job was returned from a node.
        if ('RESULTS' in data):
            tag, job = data.split(' --.-- ')
            job_type = self.deployer_jobReturns(job)
            
            # call a method that simply check if any jobs are available and tell node.
            self.deployer_dispatch(job_type)

        else: 
            print "data is :", data, ": end:"
        print"-------------------------------"        

    def message(self, message):
        self.transport.write(message + '\n')
    
    # [Deployer]
    def negotiateType(self):
        # negotiate what kind of node your are going to represent [WORKER, DATA]
        # <--- INSERT ANY LOGIC HERE TO CONTROL THE TYPE OF NODE --->
        
        # <--- END OF LOGIC -->
        log.debug('Negotiate type of client node.')
           
        # HC type CHANGE ASAP!!!
        self.message('WORKER')
        
    # [Node] Request a job relative to your type on node.    
    def node_jobRequest(self):
        log.debug('Job Requested.')
        self.message('TYPE')
        #print "jobREQ"
        self.message(str(self.factory.node._type))

    # [Deployer] Reply to a job request with the appropriate job.
    @inlineCallbacks
    def deployer_jobReply(self, job_type):
        # serve a job of the requested type...
        log.debug('Job Replied')
        if job_type == Task.Worker:
            print "SERVING THEM WORKErS!"
            job = yield node.getTask(job_type)
            
            # as soon as the job is retrieve, put it in the pending queue
            node.addPendingTask(job)
            
            # NEED TO PUT GUID FOR TASK TO ASSOCIATE IT BACK TO THEIR 
            # RESPECTIVE RESULTS!

            # serialize job
            import pickle
            job_str = pickle.dumps(job)
            self.transport.write('JOB --.-- ')
            self.transport.write(job_str + '\n')
            
        else: 
            print job_type
    
    # [Node] A Job was received.
    def node_jobReceived(self,job):
        import pickle
        job_obj = pickle.loads(job)
        
        def reply(result, task):
            # here we have the result of the job
            log.debug(str(task) + ' [result = ' + str(result) + ' ]')
            task.results = result
            task.completed = True
            
            # we need to send it back
            completed_task = pickle.dumps(task)
            
            self.transport.write('RESULTS --.-- ')
            self.transport.write(completed_task+'\n')
            

        # to execute a job!
        job_obj.d.addCallback(reply, job_obj)
        job_obj.d.callback(job_obj)
        #print "res: ", result

    # [Deployer] A job returns from a node.
    def deployer_jobReturns(self, job):
        import pickle 
        job_obj = pickle.loads(job)
        
        # need to verify (in cherry_py.py) the task guid and 
        # upon completion retrieve from pending queue and return 
        # appropriate result
        # NOT DONE YET STILL MESSING WITH PIPES AND PROCESSES SEE node_netHandle.py
        # need to re-think: getPendingTask, (the way webProtocol comms. with cloudProtocol and 
        # cherrypy) !!!!!!!
        
        task = node.getPendingTask(job_obj)
        
        if (task.completed == True):
            # success 
            log.debug(str(task) + ' was completed!')
            import os
            # returns results to the web server...
            response_str = "The result is:"+ str(task.results) +"\n"
            os.write(node._web_PIPE_Out,response_str)
        else:
            #failure
            log.debug(str(task) + ' failed!')
        return task.type
    
    # [Deployer] Dispatch any jobs
    def deployer_dispatch(self, job_type=1):
        if node._queues[job_type]:
            # jobs are still queued, dispatch information
            log.info('Jobs are available!')
            self.transport.write('DISPATCH')
        else:
            log.info('Queues are empty!')
            self.transport.write('DISPATCH none')

class CloudClientFactory(ClientFactory):

    protocol = CloudComms

    def __init__(self, deferred,node):
        self.deferred = deferred
        self.clients = []
        self.node = node

    def startedConnecting(self, connector):
        print 'Started to connect.'

    def buildProtocol(self, addr):
        print 'Connected.'
        proto = ClientFactory.buildProtocol(self, addr)
        return proto

    def clientConnectionLost(self, connector, reason):
        print 'Lost connection.  Reason:', reason
        if self.deferred is not None:
            d, self.deferred = self.deferred, None
            d.errback(reason)

    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed. Reason:', reason
        if self.deferred is not None:
            d, self.deferred = self.deferred, None
            d.errback(reason)

