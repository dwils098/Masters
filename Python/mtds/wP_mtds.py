from twisted.internet import stdio
from twisted.protocols import basic

#-------------------- Task Functionalities -----------------


def addition_function(task_obj, params):
    result = params[0] + params[1]
    
    task_obj.results = result
    return result
    
def subtract_function(task_obj, params):
    result = params[0] - params[1]
    
    task_obj.results = result
    return result

def multiply_function(task_obj, params):
    result = params[0] * params[1]
        
    task_obj.results = result
    return result

def division_function(task_obj, params):
    result = params[0] / params[1]
        
    task_obj.results = result
    return result

import rethinkdb as r
def read_file_from_db(task_obj, params):
    # first connect to the database
    pass
    # then retrieve the file...

#--------------------- End of Task Functionalities ---------


# gets request from web + process them into tasks
class WebProtocol(basic.LineReceiver):
    delimiter='\n'

    def __init__ (self, app_obj):
        self.app = app_obj
        self.buffer = ""

    def connectionMade(self):
        #self.transport.write('webProtocol --> connectionMade = SUCCESS!')
        self.app._netHandle._log.info('webProtocol --> connectionMade = SUCCESS!')

    def rawDataReceived(self, data):

        self.app._netHandle._log.debug(str(self.exp_len))

        self.buffer+=data

        
        if len(self.buffer) >= self.exp_len:
            buf = self.buffer[:self.exp_len]
            rem = self.buffer[self.exp_len:]
            

            operator, filename, data_o = str(buf).split('-',2)
            self.app._netHandle._log.debug('wP [OP] --> '+str(operator)+ ' - '+filename)
            self.app._netHandle._log.debug('wP [data] --> rawMODE  EXP_LEN = ' +str(self.exp_len) +' BUFFER_LEN = '+ str(len(self.buffer)) +' rem = '+rem)

            #+str(len(data)))
        
            from node_netHandle import Task
            
            new_task = Task("DB_STORE")
            new_task.type = Task.Data
            new_task._job_data = data_o
            new_task.create('data_process', 'save_file', [filename, 'data\binary', self.db_name, ['worker_process','retrieveData']]) 
            #self.app._netHandle._log.debug('wP [data_job] -->'+data)
            
            # create a task to save the file, and as parameters include any consequent actions.
            # in this case we want to generate a job for retrieving the data: from module = worker_process.py 
            #                                                                 function    = retrieveData
           
            
            #import base64 
            #with open(filename, 'wb') as fod:
            #    fod.write(data.decode(x'base64'))
            self.app._netHandle._log.debug('Task created: ' + str(new_task))
            self.app.addTask(new_task)
            self.app._netHandle._log.debug('Task queued! rem --> '+ rem)
            self.buffer = ""
            self.setLineMode(rem)
            return
        
        

        

    def lineReceived(self, line):
       
        result = ""
        self.app._netHandle._log.debug('wP [data] --> lineMODE ')
        self.app._netHandle._log.debug('wP [Rcvd Line] --> '+line)
        if 'store' in line:
            operator, session_id, filename,size = line.split()
            self.app._netHandle._log.debug('wP [OP] --> '+str(operator)+' - '+session_id+' - ' + filename +' - '+size)
            self.db_name = session_id
            self.exp_len = int(size)
            # change mode to receive file
            self.setRawMode()
        if 'ret' in line:
            operator, session_id, num = line.split()
            self.app._netHandle._log.debug('wP [OP] --> '+str(operator)+' - '+session_id+' - ' +str(num))
            self.db_name = session_id
            from node_netHandle import Task
            new_task = Task("DB_RETRIEVE")
            new_task.type = Task.Data
            new_task._job_data = num
            self.app._netHandle._log.debug('_job_data: ' + str(new_task._job_data) + ' --> ' + str(num))
            #import time
            #time.sleep(4)
            
            new_task.create('data_process', 'result_lookup', [self.db_name, num, ['worker_process','retrieveData_postprocessing']]) 
            self.app._netHandle._log.debug('Task created: ' + str(new_task))
            self.app.addTask(new_task)
           
        

        
        #retrieve the current file name (where the functions are defined) and strip extension
        #import os
        #module=os.path.basename(__file__).split('.', 1)[0]
        
        #self.app._netHandle._log.debug(module)
        #module = 'wP_calc'
        
        
    
        #new_task = Task("WEB")
        #new_task.type = Task.Worker        

        #if operator == 'add':
            #new_task.create(module, 'addition_function', [int(op_1), int(op_2)])
        #if operator == 'sub':
            #new_task.create(module,'subtract_function', [int(op_1), int(op_2)])
        #if operator == 'mul':
            #new_task.create(module,'multiply_function', [int(op_1), int(op_2)])
        #if operator == 'div':
            #new_task.create(module,'division_function', [int(op_1), int(op_2)])

        #self.app.addTask(new_task)

        return result
