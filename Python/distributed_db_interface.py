import Application as app

if __name__ == '__main__':

  from twisted.internet import reactor


  app_ex = app.Application("appli")

  ex_task = app.Task("Robin the Web")
  ex_task.type = app.Task.Web
  ex_task.create(app.simple_web, ["cherry_py.py",app_ex])

  ex_task_Wrk = app.Task("Robin the Worker_packed")
  ex_task_Wrk.type = app.Task.Worker
  ex_task_Wrk.create(app.ex_function, [2,2])

  ex_task_D = app.Task("Robin the Data")
  ex_task_D.type = app.Task.Data
  ex_task_D.create(app.ex_function, [3,2])



  #app_ex.addTask(ex_task)
  app_ex.addTask(ex_task_Wrk)
  app_ex.addTask(ex_task_D)

  try:
    app_ex.run()
    while(True):
      app_ex._node.printContacts()
    reactor.run()
  except KeyboardInterrupt:
    # 25 cycles without activity close web server...
    import os
    import signal

    print app_ex._web.pid
    # Send the signal to all the process groups
    #os.killpg(app_ex._web.pid, signal.SIGTERM)

    print "bye bye!"
