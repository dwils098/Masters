from twisted.web import server, resource
from twisted.internet import reactor

class WebProcess(resource.Resource):
    isLeaf = True
    def render_GET(self, request):
        return "<html>Hello, world!</html>"

site = server.Site(WebProcess())
reactor.listenTCP(8080, site)
reactor.run()
