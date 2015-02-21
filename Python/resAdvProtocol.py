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
    socket = context.socket(zmq.PUB)
    
    socket.bind("tcp://*:5556")
    
    while True: 
        topic = "cpu_usage"
        messagedata = psutil.cpu_percent(interval=0)
        print topic, messagedata
        socket.send("%s %d %s" % (topic, messagedata, guid))
        import time
        time.sleep(1)
"""
@param known_nodes is a list of the node that are known in the DHT.
"""
def seek_resources(known_nodes=["127.0.0.1"]):
    
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    
    for node_ip in known_nodes:
        address = "tcp://"+node_ip
        address += ":"
        address += "5556"
        socket.connect(address)
    
    # topic filters: cpu, ram, etc...
    topicfilter="cpu_usage"
    socket.setsockopt(zmq.SUBSCRIBE, topicfilter)

    from sets import Set
    candidates = Set()

    # hard coded threshold
    threshold=35.4 

    while True:
        string = socket.recv()
        topic, messagedata, guid = string.split()
        print topic, messagedata, guid
        x = float(messagedata)
        
        # processing of the results 
        if x < threshold:
            candidates.add(guid)
            print candidates
            break
        
    return candidates
