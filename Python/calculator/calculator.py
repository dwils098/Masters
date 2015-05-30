import node_netHandle as NODE
import sys

if __name__ == '__main__':
    import sys
    # create an application deployer node
    node = NODE.ApplicationNode(sys.argv[3],'wP_calc','web_calc.py')

    # start the logging
    from twisted.python import log
    log.startLogging(sys.stdout)
    
    # start the application
    node.run(sys.argv[1],sys.argv[2])
