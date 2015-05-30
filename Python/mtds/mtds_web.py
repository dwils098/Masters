import cherrypy



#if __name__ == '__main__' :
#  import sys
#  print "---- DataProcess ----"
#  print sys.argv
#  y = DataProcess(sys.argv[1])
#  y.start()
#  y.stop()
#        

class MTDS(object):
# def __init__(self):
#     from data_process import DataProcess
#     self.data_proc = DataProcess()
#     self.data_proc.start()

    @cherrypy.expose
    def index(self):
        if 'count' not in cherrypy.session:
            cherrypy.session['count']=0
        cherrypy.session['count']+=1

        #you'll also need to store a value in session
        cherrypy.session['Something'] = 'asdf'

        return file('web/index.html')
    
    def create_tasks(self, args, data_files):
        OP_RETRIEVE = 'ret'
        OP_STORE = 'store'
        OP_DATA = 'data'
        count = 0
        # create the tasks to store the files in the db
        for file_name, data in data_files.iteritems():
            

            import sys, time, base64
            #encode it first 
            data_str = base64.b64encode(data)
            
            output = OP_DATA + '-'+file_name+'-'+data_str+' \n'
            size = len(output)
            

            # indicate that a file is incoming...
            sys.stdout.write(OP_STORE +' ' +str(cherrypy.session.id) +' ' + file_name + ' '+ str(size))
            sys.stdout.write('\n')

            
            sys.stdout.write(output)
            count+=1


        # very nasty way to combine results...
        import time 
        time.sleep(5)

        sys.stdout.write(OP_RETRIEVE +' ' +str(cherrypy.session.id) +' ' + str(count))
        sys.stdout.write('\n')
        
        

        return 'Number of FIlES: ' + str(count)


        # print filename to be retrieved
        #for myFile in args['myFiles']:
            #print OP_RETRIEVE + ' ' + str(myFile.filename)

    @cherrypy.expose
    def upload(self,**kwargs):
        out = """<html> <body>"""

        file_out =""" myFile length: %s <br />
            myFile filename: %s <br />
            myFile mime-type: %s <br/><br/>"""

        out_close = """</body> </html>"""

        
        
        size = 0 

        # data_file dict
        data_files={}
        data_bytes=""

        list_of_files = []
        for myFile in kwargs['myFiles']:
            return_str=""
            data=""
            while True: 
                data_chunk = myFile.file.read(8192)
                if not data_chunk:
                    break
                size += len(data)
                data+=data_chunk
                
            
            # save the file as bytes
            saved = open(myFile.filename, 'wb')
            saved.write(data)
            saved.close()

            # load bytes
            loaded = open(myFile.filename, 'rb')
            data_bytes = loaded.read()
            loaded.close()

            # to the db
            data_files[str(myFile.filename)] = data_bytes
            #self.data_proc.save_file(data_bytes, str(myFile.filename), str(myFile.content_type))
            
            with open('post_'+str(myFile.filename),'wb') as fh:
                fh.write(data_files[str(myFile.filename)])
    
            return_str += file_out % (size, str(myFile.filename),str( myFile.content_type))
            
            out+=return_str

        # call task creation function
        dataa = self.create_tasks(kwargs, data_files)
        # load bytes
        
        import sys
        result = sys.stdin.readline()

        return result
        

        
# start the web_server first
cherrypy.log.screen = None
# bind to all IPv4 interfaces
cherrypy.config.update({
    'tools.sessions.on' : True,
    'server.socket_host': '0.0.0.0'
})
cherrypy.tree.mount(MTDS())
cherrypy.engine.start()
cherrypy.engine.block()
