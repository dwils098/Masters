"""
Process main class
"""
import rethinkdb as r
import time

class Process (object):

  # id starts at zero, mimicking UNIX style processes
  id_num = 0

  def __init__(self):
    # use the class provided id
    self.id = Process.id_num
    self.ip_address = '127.0.0.1'
    #increment it
    Process.id_num+=1

  def __str__(self):
    return "Process [id] = " + str(self.id)

  def _setParentNode(self, parent):
    self._parent_node = parent


"""
3 Specializations: Web, Worker, Data
"""

class WebProcess(Process):

  def __init__(self):
    super(WebProcess, self).__init__()
    self.isServerOn = False

  def __str__(self):
    return "WebProcess [id] = " + str(self.id) + " [ServerOnFlag] = " + str(self.isServerOn)

class WorkerProcess(Process):

  def __init__(self):
    super(WorkerProcess, self).__init__()
    self.busy = False

  def __str__(self):
    return "WorkerProcess [id] = " + str(self.id) + " [Busy] = " + str(self.busy)

class DataProcess(Process):
  first_node_in_cluster = True

  def __init__(self, given):
    super(DataProcess, self).__init__()
    # if DataProcess.first_node_in_cluster:
    #   self.first_node_in_cluster = True
    #   #upon creation set flag to false
    #   DataProcess.first_node_in_cluster = False
    # else:
    #   self.first_node_in_cluster = False
    self.first_node_in_cluster = given

    self.client_driver_port = 29015
    self.db_process = ""

  def __str__(self):
    return "DataProcess [id] = " + str(self.id)

  def start(self):
    print "start"
    # Default starting proceedure...
    import rethinkdb as r

    # output to log...
    from datetime import datetime
    current_date = datetime.now()
    name_of_logfile = "logs/db_log-" + str(current_date.year)+"-"+str(current_date.month)+"-"+str(current_date.day)+"-"+str(current_date.second)
    log = open(name_of_logfile,'w')

    if self.first_node_in_cluster == True:

      print "FIRST NODE"
      # then create the database..
      import os
      import signal
      from subprocess import Popen

      # The os.setsid() is passed in the argument preexec_fn so
      # it's run after the fork() and before  exec() to run the shell.
      self.db_process = Popen(['rethinkdb', '--bind', 'all'], stderr=log, preexec_fn=os.setsid)

      time.sleep(2)
      # then connect to the client driver
      r.connect(self.ip_address, self.client_driver_port).repl()

    else:

      print "NOT FIRST NODE"

      # use the existing database...
      import os
      import signal
      from subprocess import Popen

      # The os.setsid() is passed in the argument preexec_fn so
      # it's run after the fork() and before  exec() to run the shell.
      self.db_process = Popen(['rethinkdb','--port-offset', '1', '--directory', 'rethinkdb_data2','--join','127.0.0.1:29015', '--bind', 'all'], stderr=log, preexec_fn=os.setsid)

    log.flush()

  def stop(self):

    import os
    import signal

    # Send the signal to all the process groups
    os.killpg(self.db_process.pid, signal.SIGTERM)

if __name__ == '__main__' :
  import sys
  print "---- DataProcess ----"
  print sys.argv
  y = DataProcess(sys.argv[1])
  y.start()
  y.stop()
