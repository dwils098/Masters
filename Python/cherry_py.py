import cherrypy
class HelloWorld(object):
    def index(self):
        return "Hello World!"

    def not_index(self):
        return "NOT HELLO WORLD!"

    not_index.exposed = True
    index.exposed = True

# start the web_server first

cherrypy.tree.mount(HelloWorld())
cherrypy.engine.start()
cherrypy.engine.block()
