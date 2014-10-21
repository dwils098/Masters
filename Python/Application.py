from twisted.internet.defer import DeferredQueue, Deferred


################################################################################
#                        Worker USER RELATED CODE                              #
################################################################################

"""
Example function that contains application logic and is created as an compositional
part of a task.

First parameter refers to the Task object.

Second parameter refers to a list of arguments.

"""
def ex_function(task_obj, param_2):

  result = param_2[0] * param_2[1]

  print task_obj.creator

  task_obj.d.addCallback(print_result)

  return result

def print_result(result):
  print "Result is :", result


################################################################################
#                          Web USER RELATED CODE                               #
################################################################################

"""
Very simple web server using cherrypy

Simply spin a CherryPy webServer on a subprocess
"""
def simple_web(task_obj, args):
    # use the existing database...
    import os
    import signal
    from subprocess import Popen
    app = args[1]
    # The os.setsid() is passed in the argument preexec_fn so
    # it's run after the fork() and before  exec() to run the shell.
    app._web = Popen(['python','-u', args[0]])
################################################################################
#                         DATA USER RELATED CODE                               #
################################################################################




################################################################################
#                               API RELATED CODE                               #
################################################################################

# Helping function that simply fire the deferred of a task object.
def task_func (task_obj):
  # simply execute the deferred
  task_obj.d.callback(task_obj)


class Task (object):
    """
    This object represent a task in our system and it is an abstraction of an actual task.
    """
    # Task Types
    Web = 0
    Worker = 1
    Data = 2
    Undefined = 3

    def __init__(self, creator):
      self.type = Task.Undefined
      self.creator = creator
      self.completed = False
      self.d = Deferred()

    def create(self, func, args):
      # simply add a deferred
      self.d.addCallback(func,args)


class Application (object):

    """
    This object represent an application in the Cloud, and as indicated in the paper
    relating to the P2P cloud architecture proposal, these can be seen as being slices
    of cloud.

    The concept of application within this project reflect that of a container and/or a seperation
    layer from the overlay network.

    Consisting of process pool (Web/Worker/Data), and corresponding queues.

    cherry_py_instance: is the Instanciated object that contains the logic for the web_server

    """

    def __init__(self, name="app_default",port=4020):
        self._name = name
        self.number_of_nodes = 0
        self.list_of_nodes = []
        self._queues = [DeferredQueue()] * 3

        # web process pointer
        self._web = ""

        # here is the logic to join the DHT, currently using an implementation of Kademlia
        from entangled.kademlia import node

        knownNodes = [("127.0.0.1", 4020)]

        self._ip_address = "127.0.0.1"

        self._node = node.Node(4021)
        self._node.joinNetwork(knownNodes)

    def __str__(self):
        return "Application: [name] = " + self._name + " [number_of_nodes] = " + str(self.number_of_nodes)
        #" [list_of_nodes] = " + str(self.list_of_nodes)

    def addNode (self, node):
        self.list_of_nodes.append(node)
        self.number_of_nodes += 1

        # next we need to make it a process...

    def addTask (self, task):
        # simply add the task to the corresponding queue
        self._queues[task.type].put(task)

    def getTask (self, task_type):
        # simply return the top elt of the queue
        # and add a callback to fire it's deferred
        return self._queues[task_type].get().addCallback(task_func)

    def run(self):
        # attempt to read from the web queue
        print "using the run method"

        task_type = 0

        # temp variable to hold a snapshot of the number of nodes in the app.
        temp_nodes = self.number_of_nodes

        # ctr
        ctr = 0

        # then publish the name of the application that you've deployed
        self._node.iterativeStore(self._name, self._ip_address)

        # simply loop forever over each queues
        #while(True):


        """
        (1) Create any task(s) as a result of the current state of the app.
        (2) Verify the queues contents.
        (3) Prepare the task(s) to be sent to the corresponding nodes (Processes).
        (4) Send the task(s).

        ...

        (5) Wait for at least one task to complete... then start back at (1).
        """

          #self.getTask(task_type)
          #task_type += 1
          #task_type = task_type % 3
          #print "task_type = ", task_type


class ApplicationNode (object):

  """
  This class represents an ApplicationNode which can be any type of process, except
  Web because only the Application deployer can be the WebProcess as of now.
  """

  global id_count
  id_count = 0

  def __init__(self):

      self._id = id_count + 1
      self._process = ""
      self._ip_address = "127.0.0.1"
      self._port = 4023

      # here is the logic to join the DHT, currently using an implementation of Kademlia
      from entangled.kademlia import node

      knownNodes = [("127.0.0.1", 4020)]

      self._node = node.Node(self._port)
      self._node.joinNetwork(knownNodes)


  def __str__(self):
      return "ApplicationNode: [id] = " + self._id + " [ip_address] = " + str(self._ip_address) + " [port] = " + str(self._port)


  """
  Contains the logic to join an active Application in the cloud.
  """
  def joinApplication(self, app_name):
      result = self._node.iterativeFindValue(app_name)

      result.addCallback(print_result)

      return result


  def print_result(self, app_name):
      print "The result is... "

      print self[app_name]


if __name__ == '__main__':


  # create a node object
  app_node = ApplicationNode()
  #app_node.joinApplication("appli")

  from twisted.internet import reactor
  reactor.run()
