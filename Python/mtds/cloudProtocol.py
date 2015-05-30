from twisted.internet.protocol import Protocol, Factory, ClientFactory
from twisted.protocols import basic
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
        
def message(lineR, message):
    lineR.sendLine(message)


# [Deployer]
def negotiateType(lineR):
    # negotiate what kind of node your are going to represent [WORKER, DATA]
    lineR.node._netHandle._log.debug('Negotiate type of client node.')
    if lineR.node._db_nodes_num > 1:
        message(lineR,'DB_ROLE')
        lineR.node._db_nodes_num = int(lineR.node._db_nodes_num) - 1
    else:
        message(lineR,'WORKER')

# [Node] Request a job relative to your type on node.    
def node_jobRequest(lineR):
    lineR.node._netHandle._log.debug('Job Requested. -->')
    # send command
    message(lineR,'TYPE '+ str(lineR.node._type))
    # send type of job requested
    #message(lineR,str(lineR.node._type))
        
# [Deployer] Reply to a job request with the appropriate job.
@inlineCallbacks
def deployer_jobReply(lineR, job_type):
    # serve a job of the requested type...
    lineR.node._netHandle._log.debug('Job Replied')
    if job_type == Task.Worker:
        print "SERVING THEM WORKErS!"
        
    elif job_type == Task.Data:
        print 'WE HAVE A DB IN DA HOUSE!'

    else: 
        print job_type
    
    job = yield lineR.node.getTask(job_type)
        
    # as soon as the job is retrieved, put it in the pending queue
    lineR.node.addPendingTask(job)

    jbdata = job._job_data
    job._job_data = False

    # serialize job
    import pickle
    job_str = pickle.dumps(job)
    # sends task instance
    #print 'About to send this data:'
    #print jbdata

    output = 'JOB_REC --.-- ' + job_str + ' --.-- ' + str(jbdata)
    size = str(len(output))


    # signals change of mode
    message(lineR,'JOB --.-- ' +size+' \n')
    
    # start of transmission
    lineR.transport.write(output)
        

# [Node] A Job was received.
def node_jobReceived(lineR,job,job_data):
    import pickle
    job_obj = pickle.loads(job)
    
    def reply(result, task):
        # the originating job was a database storage operation, then the resulting
        # response will be the worker job to process that data.

        if task.type == Task.Data:
            # recopy the (modified) dbHandle object
            lineR.node._dbHandle = task.db

            # create a corresponding job
            new_task = Task('PROCESS_DATA')
            new_task.type = Task.Worker
            new_task._job_data = []

            # add info to retreive information
            # first IP
            new_task._job_data.append(lineR.node.ip)
            # then db_client port
            new_task._job_data.append(lineR.node._dbHandle.client_driver_port)
            # then db_name
            new_task._job_data.append(lineR.node._dbHandle.db_name)
            # then db_table
            new_task._job_data.append(lineR.node._dbHandle.db_keys[task.uuid])
            # then db_key
            new_task._job_data.append(task.uuid)
            # finally db_auth_key
            new_task._job_data.append(lineR.node._dbHandle.db_auth_key)

            # did the originating task included any instructions about post-storage processing? (psp_info)
            psp_info = result
            new_task.create(psp_info[0], psp_info[1], [
                lineR.node.ip,
                lineR.node._dbHandle.client_driver_port,
                lineR.node._dbHandle.db_name, 
                lineR.node._dbHandle.db_keys[task.uuid],
                task.uuid,
                lineR.node._dbHandle.db_auth_key
            ])
    
            lineR.node._netHandle._log.debug(new_task._job_data)

            # create new task
        

            # complete old task
            task.results = result
            task.completed = True
            task.db = False
            # after a task is complete it's data is irrelevant, only results matters.
            task._job_data = None

            # serialize the task...
            new_task_str = pickle.dumps(new_task)
            old_task_str = pickle.dumps(task)
            
            lineR.node._netHandle._log.debug('New_TASK = '+str(new_task_str))
            lineR.node._netHandle._log.debug('Old_TASK = '+str(old_task_str))

            output = 'JOB_2_B_SCHD --.-- '+old_task_str+' --.-- '+ new_task_str+'\n'
            size = str(len(output))

            # signals change of mode
            message(lineR, 'RESULTS --.-- '+ size+' \n')

            # send 
            message(lineR, output)
            
            # request another job...
            node_jobRequest(lineR)
            
            
        elif task.type == Task.Worker:
            # here we have the result of the job
            lineR.node._netHandle._log.debug(str(task) + ' [task.results = ' + str(task.results) + ' ] [result = '+ str(result)+' ]')
            #task.results = result
            task.completed = True
            task.db = False
            
            jbdata = task._job_data
            
            # after a task is complete it's data is irrelevant, only results matters.
            task._job_data = None
            
            

            # we need to send it back
            completed_task = pickle.dumps(task)
            output = 'RES_REC --.-- '+completed_task+ ' --.-- '+jbdata
            size = str(len(output))

            # signals change of mode
            message(lineR, 'RESULTS --.-- '+ size+' \n')
        
            # start of transmission
            lineR.transport.write(output)
            
            # request another job...
            node_jobRequest(lineR)

    # if job is of type Data, include dbHandle in obj in order to access it from within 
    # the task execution...
    if job_obj.type == Task.Data: 
        
        job_obj.db = lineR.node._dbHandle
        lineR.node._netHandle._log.debug(str(job_obj.db))
    
        # and extract the module name and func name for the reply job
        #module_name = job_obj.job_callback[0]
        #func_name = job_obj.job_callback[1]
    
    #lineR.node._netHandle._log.debug('received: '+job_data)
    
    job_obj._job_data = job_data
    

    
    
    # save to disk [DEBUG]
    #with open(job_obj.uuid, 'wb') as fh:
        #fh.write(job_data)

    # to execute a job!
    job_obj.d.addCallback(reply, job_obj)
    job_obj.d.callback(job_obj)
    #print "res: ", result



# [Deployer] A job returns from a node.
def deployer_jobReturns(lineR, job, job_data):
    import pickle 
    job_obj = pickle.loads(job)
    
    # need to verify (in cherry_py.py) the task guid and 
    # upon completion retrieve from pending queue and return 
    # appropriate result
    # NOT DONE YET STILL MESSING WITH PIPES AND PROCESSES SEE node_netHandle.py
    # need to re-think: getPendingTask, (the way webProtocol comms. with cloudProtocol and 
    # cherrypy) !!!!!!!
        
    task = lineR.node.getPendingTask(job_obj) 
    
    if (task.completed == True):
        # success 
        lineR.node._netHandle._log.debug(str(task) + ' was completed!')
        lineR.node._netHandle._log.debug(str(task.results))
        if task.job_callback == 'results are in':
            import os
            # returns results to the web server...
            response_str = "The result is:"+ str(task.results) +"\n"
            os.write(node._web_PIPE_Out,response_str)

    else:
        #failure
        lineR.node._netHandle._log.debug(str(task) + ' failed!')
    return task.type

# [Deployer] A job returns from a node, and creates a new one!
def deployer_jobReturnsCreate(lineR, old_job, new_job):
    import pickle 
    old_job_obj = pickle.loads(old_job)
    new_job_obj = pickle.loads(new_job)
    
    
    task = lineR.node.getPendingTask(old_job_obj) 
    
    if (task.completed == True):
        # success 
        lineR.node._netHandle._log.debug(str(old_job_obj) + ' was completed!')
        lineR.node._netHandle._log.debug(str(old_job_obj.results))
        #import os
        # returns results to the web server...
        #response_str = "The result is:"+ str(task.results) +"\n"
        #os.write(node._web_PIPE_Out,response_str)
        
        # add the new job to the queues
        lineR.node.addTask(new_job_obj)
        
    else:
        #failure
        lineR.node._netHandle._log.debug(str(old_job_obj) + ' failed!')
    return new_job_obj.type
        
# [Deployer] Dispatch any jobs
def deployer_dispatch(lineR, job_type):
    lineR.node._netHandle._log.debug('deployer_dispatch: '+str(job_type))
    if (job_type == Task.Worker) and lineR.node._w_job_count >= 1:
        # jobs are still queued, dispatch information
        lineR.node._netHandle._log.info('Jobs are available!')
        lineR.transport.write('DISPATCH \n')
    elif (job_type == Task.Data) and lineR.node._d_job_count >=1:
        # data jobs are available, dispatch information!
        lineR.node._netHandle._log.info('Jobs are available!')
        lineR.transport.write('DISPATCH \n')
    else:
        log.info('JobType = '+str(job_type))
        log.info('W_COUNT = ' +str(lineR.node._w_job_count))
        log.info('D_COUNT = ' +str(lineR.node._d_job_count))
        log.info('Queues are empty!')
        lineR.transport.write('DISPATCH none')
    

def processLine(lineR, line):
    # returns a bool representing if we need to change mode
    rawMode = False
    appD = lineR.node._appDeployer
    log = lineR.node._netHandle._log
    node = lineR.node
        

    # [Deployer] Negotiate with node what role they will accomplish.
    if('connected' in line):
        # connection is complete...
        # (1) of protocol
        if appD:
            negotiateType(lineR)
            log.info('Type has been negotiated!')
        elif not appD:
            pass
        else:
            log.error("Cannot identify whether it is an application deploying node or not")
    
    # [Node] A role was assigned to you, now request a job.
    elif('WORKER' in line):
        if not appD:
            # ok, set type then request job
            node._type = Task.Worker
            node_jobRequest(lineR)
        elif appD:
            log.error("Something's wrong this was not meant for you!")
  
    # [Node] You were assigned a DB_ROLE
    elif('DB_ROLE' in line):
        if not appD:
            # ok, set type
            node._type = Task.Data
            
            # start the db instance
            import data_process as dp 
            node._dbHandle = dp.DataProcess()
            node._dbHandle.start()

            node_jobRequest(lineR)
            log.debug("After job_request was called...")
        elif appD:
            log.error("Something's wrong this was not meant for you!")

    # [Deployer] A job was requested of a specific type
    elif ('TYPE' in line):
        log.debug(line)
        tag, job_type = line.split()
        job_type = int(job_type)
        deployer_jobReply(lineR,job_type)
    
    # [Node] A job was received, separate Tag from pickle data dump...
    elif ('JOB' in line):
        # change receiving mode
        tag,size = line.split('--.--')
        lineR.exp_len = int(size)
        rawMode = True
        
        
    # [Deployer] A job was returned from a node.
    elif ('RESULTS' in line):
        tag, size = line.split('--.--')
        lineR.exp_len = int(size)
        rawMode = True

    # [Node] Received a dispatch notice, thus a job is available, request it! 
    elif ('DISPATCH' in line):
        if not appD:
            # all queues are empty
            if 'none' in line:
                # wait 1 second and retry 
                import time 
                time.sleep(1)
                log.info('AppD has no jobs, ack it!')
                message(lineR,'BACK')
            # job available    
            else:    
                log.info('DISPATCH -- > REQUEST JOB!')
                node_jobRequest(lineR)
        else:
            log.error("Really this transporter is really confused...")
        

    # [Deployer] Dispatch bounced back retry...
    elif('BACK' in line):
        if appD:
            log.info('Recv. BACK')
            deployer_dispatch(lineR)
        else:
            log.error('The force is strong with you, young padawan, but only a true Jedi can perform this!')


    else: 
        print "line is :", line, ": end:"
    print"-------------------------------"        


       
        
        # change receiving mode
        #rawMode = True



    return rawMode

def processData(lineR, data):
    lineMode = False
    #lineR.node._netHandle._log.debug('RawDATA-REcv.: '+ str(data))
    if 'JOB_REC' in data:
        tag,job_str, job_data = str(data).split(' --.-- ',2)
        node_jobReceived(lineR,job_str,job_data)
        
        # change back to lineMode
        lineMode = True

    elif 'RES_REC' in data:
        tag, job_str, job_data = str(data).split(' --.-- ',2)
        job_type = deployer_jobReturns(lineR,job_str, job_data)
    
        # call a method that simply check if any jobs are available and tell node.
        deployer_dispatch(lineR,job_type)
    
        # change back to lineMode
        lineMode = True

    # A job was completed returned from a node, and a new job was created.
    elif 'JOB_2_B_SCHD' in data:
        tag, old_job_str, new_job_str = str(data).split(' --.-- ',2)
        job_type = deployer_jobReturnsCreate(lineR, old_job_str, new_job_str)

        # call a method that simply check if any jobs are available and tell node.
        deployer_dispatch(lineR,job_type)
        
        # change back to lineMode
        lineMode = True

    return lineMode

class CloudComms(basic.LineReceiver):
    appD = 0
    log = 0
    node = 0
    delimiter = '\n'
    def __init__(self, clients, node):
        self.clients = clients
        self.node = node
        self.buffer=""
        self.exp_len = 0

        #self.state = "GETNAME"

    def connectionMade(self):
        message(self,'connected')
        self.clients.append(self)
        print "clients are ", self.clients
        self.ctr = 0

        global appD, log,node
        appD = self.node._appDeployer
        log = self.node._netHandle._log
        node = self.node

    def connectionLost(self, reason):
        #self.factory.clients.remove(self)
        print 'Lost connection.  Reason:', reason

    def rawDataReceived(self, data):
        log.debug('cloudProtocol [data] --> rawMODE ')
        log.info("Receiving Data from %s" % self.transport.getPeer())
        #log.debug(data)
        
        self.buffer+= data
        
        log.debug('Buffer_Len: '+str(len(self.buffer))+' EXP_LEN: '+str(self.exp_len))
        val = len(self.buffer)>= int(self.exp_len)
        log.debug(str(val))
        if len(self.buffer)>= int(self.exp_len):
            log.debug('About to process some data!')
            log.debug(self.buffer)
            buf = self.buffer[:self.exp_len]
            rem = self.buffer[self.exp_len:]
            if processData(self, buf):
                self.buffer=""
                log.debug("FINISHED PROCESSING THAT DATA! "+ rem )
                self.setLineMode(rem)
                return
    
    def lineReceived(self, line):
        log.debug('cloudProtocol [data] --> rawLINE ')
        log.info("Receiving Data from %s" % self.transport.getPeer())
        log.debug('cloudProtocol [LineReceived] --> '+line)

        if processLine(self,line):
            self.setRawMode()
        
        
class CloudClientFactory(Factory):

    #protocol = CloudComms

    def __init__(self, deferred,node):
        self.deferred = deferred
        self.clients = []
        self.node = node

    def startedConnecting(self, connector):
        print 'Started to connect.'

    def buildProtocol(self, addr):
        print 'Connected.'
        #proto = ClientFactory.buildProtocol(self, addr)
        return CloudComms(self.clients, self.node)

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

