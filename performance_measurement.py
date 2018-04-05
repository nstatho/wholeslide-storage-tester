import os.path
import glob
import numpy as np
import matplotlib.pyplot as plt
import pandas
import datetime as dt

# parse log files and measure performance

def generateDicts(log_fh):
    currentDict = {}
    for line in log_fh:
        #if line.startswith("2018"):
        if "True" in line:
            if currentDict:
                yield currentDict
            currentDict = {"date": line.split("__")[0][:19], # '%Y-%m-%d %H:%M:%S'
                           "Thread": int(line.split("[")[1][7:-2]),
                           "level": line.split("[")[2][0:5],
                           "success": bool(line.split("[")[3].split(",")[0]),
                           "elapsed_time": float(line.split(",")[2]),
                           "opening_time": float(line.split(",")[3]),
                           "timestamp": line.split(",")[4].replace("'","").lstrip(), # '%Y-%m-%d %H:%M:%S'
                           "size": line.split(",")[5].replace("'","").strip("\n").strip("]").lstrip(),
                           "slide": line.split(",")[6].replace("'","").strip("\n").strip("]").lstrip()
                           }
        #else:
        #    currentDict["text"] += line
    yield currentDict

def generate_dataframe(log):
    with open(log, 'r') as f:
        try:
            prod = list(generateDicts(f)) 
        except KeyError as keyE:
            print(keyE)
        
    df = pandas.DataFrame(prod)

    df['date'] = pandas.to_datetime(df['date'], format="%Y-%m-%d %H:%M:%S")
    df['timestamp'] = pandas.to_datetime(df['timestamp'], format="%Y-%m-%d %H:%M:%S")

    df = df.set_index('timestamp')
    
    return df


##############################################################
if __name__ == "__main__":

    prod_log = '/home/nikolas/projects/slideBrowser/logs/slidebrowser_20180316_2.log'
    harry_log = '/home/nikolas/projects/slideBrowser/logs/harry.log'

    df = generate_dataframe(prod_log) 
    
    df1 = df.between_time(start_time='07:00:00', end_time = '19:00:00')
    
    df1_p = df1['elapsed_time'].resample('10Min').mean()    
                                                                    
    df_p2 = df['elapsed_time'].resample('30Min').mean()
    
                                                                    


    fig = df_p2.plot()
    pm.plt.ylim([0, 100])
    pm.plt.show()
    
    
    df_p = df['elapsed_time'].resample('60Min').mean()    
    
    fig = df_p.plot()
    pm.plt.show()

