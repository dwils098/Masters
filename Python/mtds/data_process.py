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



class DataProcess(Process):
  first_node_in_cluster = True

  def __init__(self):
    super(DataProcess, self).__init__()
    # if DataProcess.first_node_in_cluster:
    #   self.first_node_in_cluster = True
    #   #upon creation set flag to false
    #   DataProcess.first_node_in_cluster = False
    # else:
    #   self.first_node_in_cluster = False

    self.client_driver_port = 28015
    self.db_process = ""
    self.db_name = ""
    self.db_keys = {}
    self.db_auth_key = 'new_key'

  def __str__(self):
    return "DataProcess [id] = " + str(self.id)

  def start(self):
    print "start"
    # Default starting proceedure...
    import rethinkdb as r

    # output to log...
    from datetime import datetime
    current_date = datetime.now()
    name_of_logfile = "db_log-" + str(current_date.year)+"-"+str(current_date.month)+"-"+str(current_date.day)+"-"+str(current_date.second)
    
    log = open(name_of_logfile,'w')

    if  True:

      print "FIRST NODE"
      # then create the database..
      import os,sys
      import signal
      from subprocess import Popen

      # The os.setsid() is passed in the argument preexec_fn so
      # it's run after the fork() and before  exec() to run the shell.
      self.db_process = Popen(['rethinkdb', '--http-port', '6999', '--bind', 'all'], stderr=log, preexec_fn=os.setsid)

      time.sleep(2)
      # then connect to the client driver
      self.conn = r.connect('localhost', self.client_driver_port)

      # setup auth_key 
      
      #r.db('rethinkdb').table('cluster_config').get('auth').update({'auth_key': self.db_auth_key}).run(self.conn)
        
      # create table 
      try:
        result = r.table('files').run(self.conn)
      except:
        r.table_create('files', primary_key='uuid').run(self.conn)
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
        
# TASK FUNCTIONALITIES

def result_lookup(task_obj,params):
  entries = 0

  print "Number of result expected :" + str(task_obj._job_data)

  while entries >= int(task_obj._job_data):
    # this is a  blocking operation, wait for results...
    entries = r.db(params[0]).table('results').count().run(conn)
  
  print "We have " + str(entries)
  
  return params[1]
  


def save_file(task_obj,params):

  import base64
  
  #decode data
  dec_data = base64.b64decode(task_obj._job_data)
  
  # make a copy to disk
  with open(params[0], 'wb') as fh:
    fh.write(dec_data)
 
  
    
  # verify if it's the first commit to the db from this user  
  try:
    result = r.db_create(params[2]).run(task_obj.db.conn)
    # create table...
    result = r.db(params[2]).table_create('files').run(task_obj.db.conn)
    task_obj.db.db_name = params[2]
  except:
    # db already exists simply proceed...
    pass 

  

  table_name = 'files'

  r.db(params[2]).table(table_name).insert({
    'uuid': task_obj.uuid,
    'type_id': params[1],
    'filename': params[0],
    'file': r.binary(task_obj._job_data)
  }).run(task_obj.db.conn)

  # save the table name, key, 
  task_obj.db.db_keys[task_obj.uuid] = table_name

  # extract the module and func for reply job
  # where params[3][0] = module_name 
  # and   params[3][1] = func_name
  result = params[3]

  return result
