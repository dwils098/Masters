import cherrypy
class Calculator(object):
    
    @cherrypy.expose
    def index(self):
        return file('example/index.html')
    
    @cherrypy.expose
    def add(self, op_1, op_2, **params):
        print 'add',op_1, op_2
        import sys
        result = sys.stdin.readline()

        return result

    @cherrypy.expose
    def subtract(self, op_1, op_2, **params):
        print 'sub',op_1, op_2
        import sys
        result = sys.stdin.readline()

        return result
    
    @cherrypy.expose
    def multiply(self, op_1, op_2, **params):
        print 'mul',op_1, op_2
        import sys
        result = sys.stdin.readline()

        return result

    @cherrypy.expose
    def divide(self, op_1, op_2,**params):
        # send the operands to through the pipe (to the webProtocol)
        print 'div',op_1, op_2
        import sys
        
        # wait for the response...
        result = sys.stdin.readline()
        
        out = "The result is: " + result
        return out

        
# start the web_server first
cherrypy.log.screen = None
# bind to all IPv4 interfaces
cherrypy.config.update({'server.socket_host': '0.0.0.0'})
cherrypy.tree.mount(Calculator())
cherrypy.engine.start()
cherrypy.engine.block()
