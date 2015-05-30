"""
This is a simple resource advertizement mechanism, it uses a pub/sub architecture 
in which Application deployers are subscribers and the contributors are publishers 
that periodically publishes stats about their resources.
"""

import zmq
import psutil
import sys
"""
@param guid is the identifier of the advertizing node
"""
def advertize(guid="127.0.0.1"):
    port = '5556'
    
    context = zmq.Context()
    # socket to advertize resources
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://*:4444")
    
    # socket to receive a request to join an application
    rep = context.socket(zmq.REP)
    rep.bind('tcp://*:4445')
   
    poller = zmq.Poller()
    poller.register(socket, zmq.POLLOUT)
    poller.register(rep, zmq.POLLIN)
    
    should_continue = True
    
    while should_continue:

        socks = dict(poller.poll())
        if socket in socks and socks[socket] == zmq.POLLOUT:
            topic = "cpu_usage"
            messagedata = psutil.cpu_percent(interval=0)
            print topic, messagedata
            socket.send("%s %d %s" % (topic, messagedata, guid))
            import time
            time.sleep(1)
        if rep in socks and socks[rep] == zmq.POLLIN:
            mes = rep.recv()
            print mes
            if mes == 'You have been selected!':
                should_continue = False
                rep.send('Ok, waiting further instructions!')

    # you have been selected now wait until the application deployer is done selecting...
    waiting = True
    while waiting:
        socks = dict(poller.poll())
        if rep in socks and socks[rep] == zmq.POLLIN:
            mes = rep.recv()
            print mes
            if mes == 'READY, SET, GO!':
                waiting = False
        
        
"""
@param known_nodes is a list of the node that are known in the DHT.
"""
def seek_resources(known_nodes=["127.0.0.1"]):
    print "SEEEEK IT "
    
    context = zmq.Context()
    # socket to seek resources
    socket = context.socket(zmq.SUB)
    
    for node_ip in known_nodes:
        address = "tcp://"+node_ip
        address += ":"
        address += "4444"
        socket.connect(address)
    
    # topic filters: cpu, ram, etc...
    topicfilter="cpu_usage"
    socket.setsockopt(zmq.SUBSCRIBE, topicfilter)

    # socket to inform the node that it has been selected
    req = {}
    
    for node_ip in known_nodes:
        req[node_ip] =  context.socket(zmq.REQ)
    
    for node_ip in known_nodes:
        address = "tcp://"+node_ip
        address += ":"
        address += "4445"
        print address
        req[node_ip].connect(address)
    
    from sets import Set
    candidates = Set()

    # hard coded threshold
    threshold=65.4 
    number_of_nodes = 2
    num = 0

    while num<number_of_nodes:
        string = socket.recv()
        topic, messagedata, guid = string.split()
        print topic, messagedata, guid
        x = float(messagedata)
        
        # processing of the results 
        if x < threshold and guid not in candidates:
            req[guid].send('You have been selected!')
            candidates.add(guid)
            num=num+1
            print candidates
            # receive ack
            ack = req[guid].recv()
            print ack
    
    # you have the desired number of nodes, 
    # now notify them and start app...
    for candidate in candidates:
        req[candidate].send('READY, SET, GO!')
    return candidates
