from twisted.internet import stdio
from twisted.protocols import basic

# gets request from web + process them into tasks
class WebProtocol(basic.LineReceiver):
    from os import linesep as delimiter

    def __init__ (self, app_obj):
        self.app = app_obj

    def connectionMade(self):
        #self.transport.write('webProtocol --> connectionMade = SUCCESS!')
        self.app._netHandle._log.info('webProtocol --> connectionMade = SUCCESS!')

    def lineReceived(self, line):
       
        self.app._netHandle._log.debug('wP --> '+line)

        result = ""
        op_1, op_2 = line.split()
        
        from node_netHandle import Task, ex_function
        print " op_1 = ", op_1,' op_2 = ', op_2
        new_task = Task("WEB")
        new_task.type = Task.Worker
        new_task.create(ex_function, [int(op_1), int(op_2)])
        
        def response(results):
            print "RESPONSE! --> ", results
            self.transport.write(results)
        # add a callback to the response
        #new_task.d.addCallback(response)

        self.app.addTask(new_task)

        #self.transport.write()
        return result
