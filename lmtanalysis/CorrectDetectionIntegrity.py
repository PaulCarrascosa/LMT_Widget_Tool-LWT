'''

@author: Fab

In case of a nest, for instance, 2 animals can be seen as one detection. Which is wrong.
in that case only one animal is observed and this should not be considered in other labeling.

The purpose of this code is to remove those faulty situation by switching the identity of animals involved in such situation to anonymous.

This script should not be ran if there is occlusion in the scene. This script assumes all animals could be watched all the time.

WARNING: 
This script alters the lmtanalysis:
After running this script detection at t without all identity recognized will be all switched to anonymous !

'''
import sqlite3
from time import *

from lmtanalysis.Animal import *
from lmtanalysis.Detection import *
from lmtanalysis.Measure import *
import matplotlib.pyplot as plt
import numpy as np
from lmtanalysis.Event import *
from lmtanalysis.Measure import *
from lmtanalysis.Chronometer import Chronometer
from lmtanalysis.FileUtil import getFilesToProcess

def loadDetectionMap(connection, animal, start=None, end=None):
    
        chrono = Chronometer("Correct detection integrity: Load detection map")
        print("processing animal ID: {}".format(animal))

        result = {}
        
        cursor = connection.cursor()
        query = "SELECT FRAMENUMBER FROM DETECTION WHERE ANIMALID={}".format(animal)

        if (start != None):
            query += " AND FRAMENUMBER>={}".format(start)
        if (end != None):
            query += " AND FRAMENUMBER<={}".format(end)
            
        print(query)
        cursor.execute(query)
        
        rows = cursor.fetchall()
        cursor.close()    
        
        for row in rows:
            frameNumber = row[0]
            result[frameNumber] = True;
        
        print(" detections loaded in {} seconds.".format(chrono.getTimeI()))
        
        return result


def correct(connection, tmin=None, tmax=None):
    
    pool = AnimalPool( )
    pool.loadAnimals( connection )
    #pool.loadDetection( start = tmin, end = tmax )

    cursor = connection.cursor()

    if tmin is None:
        query = "SELECT MIN(FRAMENUMBER) FROM FRAME"
        cursor.execute(query)
        minFrames = cursor.fetchall()
        for minFrame in minFrames:
            tmin = minFrame[0]

    if tmax is None:
        query = "SELECT MAX(FRAMENUMBER) FROM FRAME"
        cursor.execute(query)
        maxFrames = cursor.fetchall()
        for maxFrame in maxFrames:
            tmax = maxFrame[0]

    #Select the MAX ID of DETECTION
    query = "SELECT MAX(ID) FROM DETECTION"
    cursor.execute(query)
    maxIDtemp = cursor.fetchall()
    maxID = maxIDtemp[0][0]
    print(maxID)

    '''
    get the number of expected animals
    if there is not all detections expected, switch all to anonymous
    '''
    
    validDetectionTimeLine = EventTimeLine(None, "IDs integrity ok", None, None, None, None, loadEvent=False)
    validDetectionTimeLineDictionnary = {}

    detectionTimeLine = {}

    for idAnimal in pool.getAnimalDictionnary():
        detectionTimeLine[idAnimal] = loadDetectionMap(connection, idAnimal, tmin, tmax)

    for t in range(tmin, tmax +1):
        
        valid = True
        for idAnimal in detectionTimeLine.keys():
            if not (t in detectionTimeLine[idAnimal]):
                valid = False
        if (valid):
            validDetectionTimeLineDictionnary[t] = True
    
    '''
    rebuild detection set
    '''
    
    #cursor = connection.cursor()

    countCorrection = 0

    for idAnimal in detectionTimeLine.keys():
        for t in range ( tmin , tmax +1 ):
            if ( t in detectionTimeLine[idAnimal] ):
                if not ( t in validDetectionTimeLineDictionnary ):
                    query = "UPDATE `DETECTION` SET `ANIMALID`=NULL WHERE `FRAMENUMBER`='{}';".format( t )
                    cursor.execute( query )
                    print ( f"{countCorrection}: {query}" )
                    countCorrection += 1
    
    connection.commit()
    cursor.close()
    validDetectionTimeLine.reBuildWithDictionnary( validDetectionTimeLineDictionnary )
    validDetectionTimeLine.endRebuildEventTimeLine(connection )

    print(f" =>  THERE WERE {countCorrection} CORRECTIONS IN THE DATABASE")
    print(f" This represents approximately {countCorrection/maxID*100}% of Alteration of the database")

    # log process
    from lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger(connection)
    t.addLog("Correct detection integrity", tmin=tmin, tmax=tmax)

       
    print( "Rebuild event finished." )


if __name__ == '__main__':
    files = getFilesToProcess()

    for file in files:
        print("Processing file", file)
        connection = sqlite3.connect(file)  # connect to database
        animalPool = AnimalPool()  # create an animalPool, which basically contains your animals
        animalPool.loadAnimals(connection)  # load infos about the animals

        correct(connection)

        connection.close()

    print("******* ALL JOBS DONE !!! *******")

