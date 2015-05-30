import cherrypy
class Calculator(object):
    #def __init__(self, node):
    #    self.node = node
    
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
        #print self
        # send the operands to through the pipe (to the webProtocol)
        print 'div',op_1, op_2
        import sys
        
        result = sys.stdin.readline()
        #print result
        #pagestr="<html>"+"<body>"+"<p>"+ str(int(op_1) *int(op_2)) + "<\\p>"+ "<\\body>"+ "<\\html>"
        return result

        
# start the web_server first
cherrypy.log.screen = None
# bind to all IPv4 interfaces
cherrypy.config.update({'server.socket_host': '0.0.0.0'})
cherrypy.tree.mount(Calculator())
cherrypy.engine.start()
cherrypy.engine.block()
