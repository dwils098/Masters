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
    from os import linesep as delimiter

    def __init__ (self, app_obj):
        self.app = app_obj

    def connectionMade(self):
        self.app._netHandle._log.info('webProtocol --> connectionMade = SUCCESS!')

    def lineReceived(self, line):
       
        self.app._netHandle._log.debug('wP --> '+line)

        result = ""
        operator,op_1, op_2 = line.split()
        
        #retrieve the current file name and strip extension
        import os
        module=os.path.basename(__file__).split('.', 1)[0]
        
        self.app._netHandle._log.debug(module)
        
        from node_netHandle import Task

        new_task = Task("WEB")
        new_task.type = Task.Worker        

        if operator == 'add':
            new_task.create(module, 'addition_function', [int(op_1), int(op_2)])
        if operator == 'sub':
            new_task.create(module,'subtract_function', [int(op_1), int(op_2)])
        if operator == 'mul':
            new_task.create(module,'multiply_function', [int(op_1), int(op_2)])
        if operator == 'div':
            new_task.create(module,'division_function', [int(op_1), int(op_2)])

        self.app.addTask(new_task)

        return result
