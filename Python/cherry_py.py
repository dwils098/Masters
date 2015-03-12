import cherrypy
class HelloWorld(object):
    #def __init__(self, node):
    #    self.node = node
    
    @cherrypy.expose
    def index(self):
        return file('example/index.html')
    
    @cherrypy.expose
    def compute(self, op_1, op_2,**params):
        #print self
        print op_1, op_2
        import sys
        
        result = sys.stdin.readline()
        print result
        #return "<html>"+
        #       "<body>"+
        #       "<p>"+
        #       
        #       "<\p>"+ 
        #       "<\body>"+
        #       "<\html>"
        
# start the web_server first
cherrypy.log.screen = None
cherrypy.tree.mount(HelloWorld())
cherrypy.engine.start()
cherrypy.engine.block()
