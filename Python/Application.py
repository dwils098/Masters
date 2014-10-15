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
Example function that contains application logic and is created as an compositional
part of a task.

Spins a Web server

First parameter refers to the Task object.

Second parameter refers to a list of arguments.

"""
def init_web(task_obj, args):

  from twisted.web import server, resource
  from twisted.internet import reactor

  class WebProcess(resource.Resource):
      isLeaf = True
      def render_GET(self, request):
          headers = request.getAllHeaders()
          html_str = "<html> "
          for header in headers:
            html_str += (header + "\n")

          html_str += "ip: " +request.getClientIP() + "\n"
          html_str += "user: " + request.getUser()
          html_str += "</html>"
          return html_str


  root = WebProcess()

  import hello
  root.putChild('hello', Hello())
  site = server.Site(root)
  reactor.listenTCP(8189, site)

  print task_obj.creator
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
    """

    def __init__(self, name="app_default"):
        self.name = name
        self.number_of_nodes = 0
        self.list_of_nodes = []
        self._queues = [DeferredQueue()] * 3


    def __str__(self):
        return "Application: [name] = " + self.name + " [number_of_nodes] = " + str(self.number_of_nodes)
        #" [list_of_nodes] = " + str(self.list_of_nodes)

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
        self.getTask(Task.Worker)
        self.getTask(Task.Web)
        self.getTask(Task.Data)



if __name__ == '__main__':

  from twisted.internet import reactor


  app = Application()

  ex_task = Task("Robin the Web")
  ex_task.type = Task.Web
  ex_task.create(init_web, [])

  ex_task_Wrk = Task("Robin the Worker")
  ex_task_Wrk.type = Task.Worker
  ex_task_Wrk.create(ex_function, [2,2])

  ex_task_D = Task("Robin the Data")
  ex_task_D.type = Task.Data
  ex_task_D.create(ex_function, [3,2])

  app.addTask(ex_task)
  app.addTask(ex_task_Wrk)
  app.addTask(ex_task_D)

  app.run()

  reactor.run()
