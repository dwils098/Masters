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
#--------------------- End of Task Functionalities ---------

# This class takes requests in from the webServer + process them into tasks
class WebProtocol(basic.LineReceiver):
    delimiter='\n'

    def __init__ (self, app_obj):
        self.app = app_obj
        self.buffer = ""

    def connectionMade(self):
        self.app._netHandle._log.info('webProtocol --> connectionMade = SUCCESS!')

    def rawDataReceived(self, data):
        self.app._netHandle._log.debug(str(self.exp_len))

        self.buffer+=data

        if len(self.buffer) >= self.exp_len:
            buf = self.buffer[:self.exp_len]
            rem = self.buffer[self.exp_len:]
            
            operator, filename, data_o = str(buf).split('-',2)
            
            from node_netHandle import Task
            
            new_task = Task("DB_STORE")
            new_task.type = Task.Data
            new_task._job_data = data_o
            new_task.create('data_process', 
                            'save_file', 
                            [filename, 'data\binary', 
                             self.db_name, 
                             ['worker_process','retrieveData']]) 
            
            # create a task to save the file, and as parameters 
            # include any consequent actions. In this case we want 
            # to generate a job for retrieving the data: 
            #             from module = worker_process.py 
            #             function    = retrieveData
           
            self.app.addTask(new_task)
            self.buffer = ""
            self.setLineMode(rem)
            return

    def lineReceived(self, line):
       
        result = ""
        if 'store' in line:
            operator, session_id, filename,size = line.split()
            self.db_name = session_id
            self.exp_len = int(size)
            # change mode to receive file
            self.setRawMode()
        if 'ret' in line:
            operator, session_id, num = line.split()
            self.db_name = session_id
            from node_netHandle import Task
            new_task = Task("DB_RETRIEVE")
            new_task.type = Task.Data
            new_task._job_data = num

            new_task.create('data_process', 
                            'result_lookup', 
                            [self.db_name, num, 
                             ['worker_process','retrieveData_postprocessing']]) 

            self.app.addTask(new_task)
        return result
