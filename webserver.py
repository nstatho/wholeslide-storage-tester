# webserver.py

import subprocess
from cherrypy import wsgiserver
import select
import getopt
import os,os.path
import sys

def main(argv):
    logfile = []
    port = [] 
    try:
      opts, args = getopt.getopt(sys.argv[1:],"hp:l:",["-p", "-l"])
    except getopt.GetoptError:
      print('webserver.py -p 8000 -l </path/to/logfile.log> ')
      sys.exit(2)
    for opt, arg in opts:
      if opt == '-h':
         print('webserver.py -p 8000 -l </path/to/logfile.log> ')
         sys.exit()
      elif opt in ("-l"):
         logfile = arg
      elif opt in ("-p"):
          port = int(arg)
      else:
         assert False, "unhandled option"    
    return port, logfile


def application(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain')])
    #proc = subprocess.Popen(['python3', 'slideBrowser.py'], stdout=subprocess.PIPE)

    #logfile = get_logfile()
    #filename = 'slidebrowser.log'
    f = subprocess.Popen(['tail','-F',logfile],\
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    p = select.poll()
    p.register(f.stdout)
        
    line = f.stdout.readline()
    while line:
        yield line
        line = f.stdout.readline()

if __name__ == "__main__":
    global logfile
    port, logfile = main(sys.argv[1:-1]) 
    #print(port)
    #print(logfile)
    
    server = wsgiserver.CherryPyWSGIServer(('0.0.0.0', port), application)
    server.start()
