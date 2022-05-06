import csv
import os
import time
import datetime

rootPath = os.path.abspath("MTF_XML_to_CSV")
#rootPath = os.getcwd().split('Desktop')[0] + '\\Desktop\\MTF_XML_to_CSV'
logFileName = rootPath + '\\parseLog' + time.strftime("%Y%m%d") + '.log'

import pandas as pd

import uuid
import logging

import configparser
import psycopg2
import numpy
import packaging, packaging.version, packaging.markers # needed since Python 3.5
import packaging.requirements, packaging.specifiers, packaging.utils
import pbr
import six.moves
from six.moves import urllib
from six.moves.urllib import parse
import multiprocessing
from errno import EEXIST, ENOENT
from hashlib import md5
from posixpath import join as urljoin
from threading import Thread
from six import Iterator, StringIO, string_types, text_type
from six.moves.queue import Queue
from six.moves.queue import Empty as QueueEmpty
from six.moves.urllib.parse import quote
import json
import requests
from threading import Timer,Thread,Event

import xml.etree.ElementTree as ET
timestr = time.strftime("%Y%m%dT%H%M%S")

logging.basicConfig(filename=logFileName, filemode='a', level=logging.INFO , format='%(levelname)s - %(name)s - %(asctime)-15s - %(message)s')
logging.info('started')

def processInput():
    if not os.listdir(rootPath + '\\inputXML'):
        return
    
    fileNameID = str(uuid.uuid1())
    
    os.mkdir(rootPath + '\\' + fileNameID)
    
    outputFile = (rootPath +'\\'+ fileNameID +'\\'+ fileNameID + ".csv")


    serial=''
    station=''
    operator=''
    version=''

    metrics = []
    

    with open(rootPath + '\\parseConfig.csv', 'r') as file:
        csvReader = csv.reader(file, delimiter =str(','))
        for row in csvReader:
            if row[0] == 'SerialNumber':
                serial = row[1]
            elif row[0] == 'StationID':
                station = row[1]
            elif row[0] == 'Operator':
                operator = row[1]
            elif row[0] == 'DataProcessVersion':
                version = row[1]
                
    outputCSV = open(outputFile, 'w', newline='')
    csvwriter = csv.writer(outputCSV)
    outputHead=["UUID","TestItem","TestValue"]
    csvwriter.writerow(outputHead)
    csvwriter.writerow([fileNameID, 'SerialNumber', serial])        
    csvwriter.writerow([fileNameID, 'StationID', station])        
    csvwriter.writerow([fileNameID, 'Operator', operator])            
    csvwriter.writerow([fileNameID, 'DataProcessVersion', version])        
    csvwriter.writerow([fileNameID, 'ProcessingStartTime', timestr])
    csvwriter.writerow([fileNameID, 'ProcessingEndTime', timestr])

    for root, dirs, files in os.walk(rootPath+"\\inputXML"):
        for name in files:
            if str(name).endswith('.xml'):
                print('xml found: ' + str(name))
                color = ''
                tree = ET.parse(rootPath+"\\inputXML\\" + name)
                rootXML = tree.getroot()
                for setup in rootXML.iter('setup'):
                    color = setup.get('color')
                for sample in rootXML.iter('sample'):
                    sampleNum = sample.get('number')
                    for ext in sample.iter('exit'):
                        exitNum = ext.get('number')
                        for camera in ext.iter('camera'):
                            index = (camera.get('index'))
                            mtfXString = (camera.get('sag_curve'))
                            mtfYString = (camera.get('tan_curve'))
                            tiltX = (camera.get('ray_tilt_x'))
                            tiltY = (camera.get('ray_tilt_y'))
                            if index == '1' and mtfXString and mtfYString:
                                sMetric=[]
                                sMetric.append(name)
                                mtfX = list(map(float,mtfXString.split(',')))
                                mtfY = list(map(float,mtfYString.split(',')))
                        
                                infoString = color + "_Sample#" + str(sampleNum)+"_Exit#"+str(exitNum)+"_Camera#"+str(index)
                                csvwriter.writerow([fileNameID,"MTF_x@15lp/deg_" + infoString , str(mtfX[15]/100)])
                                csvwriter.writerow([fileNameID,"MTF_y@15lp/deg_" + infoString , str(mtfY[15]/100)])
                                resX = next(x for x, val in enumerate(mtfX) if val < 30)
                                csvwriter.writerow([fileNameID,"MTF30_x@index_" + infoString , str(resX)])
                                resY = next(x for x, val in enumerate(mtfY) if val < 30)
                                csvwriter.writerow([fileNameID,"MTF30_y@index_" + infoString , str(resY)])
            
                                csvwriter.writerow([fileNameID,"CRA_x_fromraytilt(arcmin)_" + infoString , str(float(tiltX) / 60)])
                                csvwriter.writerow([fileNameID,"CRA_y_fromraytilt(arcmin)_" + infoString , str(float(tiltY) / 60)])
                                sMetric.append(color)
                                sMetric.append(str(sampleNum))
                                sMetric.append(str(exitNum))
                                
                                sMetric.append(index)
                                sMetric.append(str(mtfX[15]/100))
                                sMetric.append(str(mtfY[15]/100))
                                sMetric.append(str(resX))
                                sMetric.append(str(resY))
                                sMetric.append(str(float(tiltX) / 60))
                                sMetric.append(str(float(tiltY) / 60))
                                metrics.append(sMetric)
                
                    
            logging.info(name + " added to CSV")
            
            newPath = rootPath +'\\'+ fileNameID + "\\" + name
            os.replace(rootPath+"\\inputXML\\" + name, newPath)        
            
    metricColumns = ["name","Color","Sample#","Exit#","Camera#","MTF15X","MTF15Y","MTF30X", "MTF30Y","ray_tilt_x","ray_tilt_y"]        
    dfMetrics = pd.DataFrame(data = metrics, columns = metricColumns)
    print(fileNameID + ".csv was created")
    outputCSV.close()
class HourlyCheck(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            print("Hourly Check: " + time.strftime("%Y%m%dT%H%M%S"))
            self.function(*self.args, **self.kwargs)
            
            #processInput()
print('Processing loop started, press ctrl+c to exit')
processInput()

delta = datetime.timedelta(hours=1)
now = datetime.datetime.now()
next_hour = (now + delta).replace(microsecond=0, second=0, minute=0)
diff_seconds = (next_hour - now).seconds

try:
    time.sleep(diff_seconds)
except KeyboardInterrupt:
    logging.info("finished")
    os._exit(0)
print("Hourly Check: " + time.strftime("%Y%m%dT%H%M%S"))
processInput()

timer = HourlyCheck(3600,processInput)
timer.start()
try:
    while True:
        time.sleep(5)
except KeyboardInterrupt:
    timer.cancel()

logging.info("finished")

#input("press any key to exit")
        