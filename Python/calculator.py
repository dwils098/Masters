import node_netHandle as NODE
import sys

if __name__ == '__main__':

    # create an application deployer node
    node = NODE.ApplicationNode('True')

    # start the logging
    from twisted.python import log
    log.startLogging(sys.stdout)
    
    # start the application
    ip = '127.0.0.1'
    port = '5557'
    node.run(ip,port)
