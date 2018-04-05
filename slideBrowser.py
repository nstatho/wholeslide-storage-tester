import logging
import time
from time import gmtime, strftime
import multiprocessing.pool as mp
from multiprocessing.pool import ThreadPool
import sys
import os,os.path
import getopt
import openslide
import itertools


def main(argv):
    logfile = []
    pacs_dir = []   
    try:
      opts, args = getopt.getopt(sys.argv[1:],"ha:l:",["-a","-l"])
    except getopt.GetoptError:
      print('slideBrowser.py -a </path/to/archive.txt> -l </path/to/save_location/logfile.log> ')
      sys.exit(2)
    for opt, arg in opts:
      if opt == '-h':
         print('slideBrowser.py -a </path/to/archive.txt> -l </path/to/save_location/logfile.log> ')
         sys.exit()
      elif opt in ("-a"):
         pacs_dir = arg
      elif opt in ("-l"):
         logfile = arg
      else:
         assert False, "unhandled option"    
    return pacs_dir, logfile


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
def humansize(nbytes):
    i = 0
    while nbytes >= 1024 and i < len(suffixes)-1:
        nbytes /= 1024.
        i += 1
    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (f, suffixes[i])


def browseSlide(slide):
    start = time.time()
    
    success = False    
    try:
        time_to_open = time.time()
        image = openslide.open_slide(slide)
        time_to_open_end = time.time()        
        levels = [0,1,2]    
        for level in levels:
            #if ((time.time() - start) > 10):
            #    logging.info('delay detected retrieving patch from slide: %s', slide)
            image_patch = image.read_region( (0,0), level, (512,512))
        image.close()
        success = True
    except OSError as err:        
        logging.error("OS error: {0}".format(err))
    
    end = time.time()
    elapsed_time = end - start
    time_to_open_slide = time_to_open_end - time_to_open
    timestamp = strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    result = [success, elapsed_time, time_to_open_slide, timestamp, humansize(os.path.getsize(slide)), slide]
    logging.info(result)
    return result
    

result_list = []
def log_result(result):
    # This is called whenever foo_pool(i) returns a result.
    # result_list is modified only by the main process, not the pool workers.
    result_list.append(result)    
    #logging.info(result)    

########################################################################
########################################################################


if __name__ == "__main__":

    MAX_WORKERS = 1
    
    pacs_dir, logfile = main(sys.argv[1:-1])      
    
    #logPath, fileName = os.path.split(logfile)
            
    logging.basicConfig(
        format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
        level=logging.INFO,
        handlers=[
            #logging.FileHandler("{0}/{1}".format(logPath, fileName)),
            logging.FileHandler("{0}".format(logfile)),
            logging.StreamHandler()
        ])


    # import the slide list
    pacs_archive = []
    #pacs_dir = 'pacs_archive.txt'

    try:
        with open(pacs_dir, 'r') as f:
            for line in f.readlines():
                pacs_archive.append(line.strip('\n'))
    except OSError as err:
        #print("OS error: {0}".format(err))
        logging.error("OS error: {0}".format(err))


    logging.info('Start slide browsing')
    chunked_archive = chunks(pacs_archive, MAX_WORKERS)

    while True:    
        for archive in itertools.cycle(chunked_archive):
            #archive = next(chunked_archive)
            #pool = mp.Pool(processes = MAX_WORKERS)        
            pool = ThreadPool(8)
            for slide in archive:            
                pool.apply_async(browseSlide, args = (slide, ), callback = log_result)                
            pool.close()
            pool.join()
            time.sleep(2)
           
    logging.debug('exit') 
 


