import cherrypy

class MTDS(object):

    @cherrypy.expose
    def index(self):
        if 'count' not in cherrypy.session:
            cherrypy.session['count']=0
        cherrypy.session['count']+=1

        # to store a value in session
        cherrypy.session['Something'] = 'else...'

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
            sys.stdout.write(OP_STORE +
                             ' ' +str(cherrypy.session.id) +
                             ' ' + file_name + ' '+ str(size))
            sys.stdout.write('\n')
            sys.stdout.write(output)
            count+=1

            
        
        sys.stdout.write(OP_RETRIEVE +' ' +str(cherrypy.session.id) +' ' + str(count))
        sys.stdout.write('\n')
        
        return 'Number of FIlES: ' + str(count)

    @cherrypy.expose
    def upload(self,**kwargs):
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
            with open('post_'+str(myFile.filename),'wb') as fh:
                fh.write(data_files[str(myFile.filename)])
    
        # call task creation function
        count = self.create_tasks(kwargs, data_files)

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
