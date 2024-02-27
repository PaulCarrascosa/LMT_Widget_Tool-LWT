import sys
sys.path.insert(1, "../")

import sqlite3
import os
from tqdm import tqdm
from time import *
import datetime
import matplotlib.pyplot as plt
import traceback
import numpy as np
import pandas as pd
import warnings
warnings.simplefilter(action='ignore')

from lmtanalysis.Util import *
from lmtanalysis.Animal import *
from lmtanalysis.Event import *
from lmtanalysis.Measure import *
from lmtanalysis.BuildEventNight import *
from lmtanalysis import BuildEventApproachContact, BuildEventOtherContact, BuildEventPassiveAnogenitalSniff, \
    BuildEventHuddling, BuildEventTrain3, BuildEventTrain4, BuildEventTrain2, BuildEventFollowZone, BuildEventRear5, \
    BuildEventCenterPeripheryLocation, BuildEventRearCenterPeriphery, BuildEventFloorSniffing, BuildEventSocialApproach, \
    BuildEventSocialEscape, BuildEventApproachContact, BuildEventOralOralContact, BuildEventApproachRear, \
    BuildEventGroup2, BuildEventGroup3, BuildEventGroup4, BuildEventOralGenitalContact, BuildEventStop, \
    BuildEventWaterPoint, BuildEventMove, BuildEventGroup3MakeBreak, BuildEventGroup4MakeBreak, BuildEventSideBySide, \
    BuildEventSideBySideOpposite, BuildEventDetection, BuildDataBaseIndex, BuildEventWallJump, BuildEventSAP, \
    BuildEventOralSideSequence, CheckWrongAnimal, CorrectDetectionIntegrity, BuildEventNest4, BuildEventNest3, \
    BuildEventGetAway
from psutil import virtual_memory
from tkinter.filedialog import askopenfilename
from lmtanalysis.TaskLogger import TaskLogger
from lmtanalysis.FileUtil import getFilesToProcess
from lmtanalysis.EventTimeLineCache import flushEventTimeLineCache, \
    disableEventTimeLineCache, EventTimeLineCached

# --------------------------------------------------------------------------------------------------------
# Start of rebuild
# --------------------------------------------------------------------------------------------------------

# Select databases to rebuild and create csv
files = getFilesToProcess()

count = 0

''' minT and maxT to process the analysis (in frame) '''
minT = 0

# maxT = 5000
maxT = 72 * oneHour
# maxT = (6+1)*oneHour
''' time window to compute the events. '''
# windowT = 1 * oneHour
windowT = 1 * oneDay
# windowT = 3*oneDay #int (0.5*oneDay)

USE_CACHE_LOAD_DETECTION_CACHE = True

class FileProcessException(Exception):
    pass

'''Few events must be created with others like Move which must be activated with Stop events because Move events are 
created in relation to Stop events '''

eventClassList = [
                # # BuildEventHuddling,
                BuildEventDetection,
                BuildEventStop,
                BuildEventMove,
                BuildEventOralOralContact,
                BuildEventOralGenitalContact,
                BuildEventSideBySide,
                BuildEventSideBySideOpposite,
                BuildEventTrain2,
                BuildEventTrain3,
                # BuildEventTrain4,
                BuildEventFollowZone,
                BuildEventRear5,
                BuildEventCenterPeripheryLocation,
                BuildEventRearCenterPeriphery,
                BuildEventSocialApproach,
                BuildEventGetAway,
                BuildEventSocialEscape,
                BuildEventApproachRear,
                BuildEventGroup2,
                BuildEventGroup3,
                # BuildEventGroup4,
                BuildEventGroup3MakeBreak,
                # BuildEventGroup4MakeBreak,
                # BuildEventWaterPoint,
                BuildEventApproachContact,
                # BuildEventWallJump,
                BuildEventSAP,
                BuildEventOralSideSequence,
                BuildEventNest3,
                # BuildEventNest4
                   ]

# eventClassList = [BuildEventStop]

# eventClassList = [BuildEventPassiveAnogenitalSniff, BuildEventOtherContact, BuildEventExclusiveSideSideNoseAnogenitalContact]
# eventClassList = [BuildEventApproachContact2]

'''eventClassList = [

                BuildEventDetection,
                BuildEventMove,
                BuildEventRear5,
                BuildEventCenterPeripheryLocation,
                BuildEventRearCenterPeriphery,
                BuildEventStop,
                BuildEventWaterPoint,
                BuildEventWallJump,
                BuildEventSAP
                   ]'''

def flushNightEvents(connection):
    ''' flush 'NIGHT' event in database '''
    # print("delete night in DBs ?")
    deleteEventTimeLineInBase(connection, "night")

def flushEvents( connection ):

    for ev in eventClassList:

        chrono = Chronometer( "Flushing event " + str(ev) )
        ev.flush( connection );

def processTimeWindow(connection, file, currentMinT, currentMaxT):
    CheckWrongAnimal.check(connection, tmin=currentMinT, tmax=currentMaxT)

    # Warning: enabling this process (CorrectDetectionIntegrity) will alter the database permanently
    # CorrectDetectionIntegrity.correct(connection, tmin=0, tmax=maxT)

    # BuildEventDetection.reBuildEvent(connection, file, tmin=currentMinT, tmax=currentMaxT)

    animalPool = None

    flushEventTimeLineCache()

    if (USE_CACHE_LOAD_DETECTION_CACHE):
        animalPool = AnimalPool()
        animalPool.loadAnimals(connection)
        animalPool.loadDetection(start=currentMinT, end=currentMaxT)

    for ev in eventClassList:
        chrono = Chronometer(str(ev))
        ev.reBuildEvent(connection, file, tmin=currentMinT, tmax=currentMaxT, pool=animalPool)

def process(file):

    mem = virtual_memory()
    availableMemoryGB = mem.total / 1000000000

    if availableMemoryGB < 10:
        disableEventTimeLineCache()

    chronoFullFile = Chronometer("File " + file)

    connection = sqlite3.connect(file)

    try:
        connection = sqlite3.connect(file)
        c = connection.cursor()
        query = "ALTER TABLE EVENT ADD METADATA TEXT";
        c.execute(query)
        connection.commit()

    except Exception as e:
        pass

    BuildDataBaseIndex.buildDataBaseIndex(connection, force=False)
    # build sensor data
    animalPool = AnimalPool()
    animalPool.loadAnimals(connection)

    currentT = minT
    try:
        flushEvents(connection)
        while currentT < maxT:
            currentMinT = currentT
            currentMaxT = currentT + windowT
            if (currentMaxT > maxT):
                currentMaxT = maxT
            chronoTimeWindowFile = Chronometer(
                "File " + file + " currentMinT: " + str(currentMinT) + " currentMaxT: " + str(currentMaxT));
            processTimeWindow(connection, file, currentMinT, currentMaxT)
            # chronoTimeWindowFile.printTimeInS()
            currentT += windowT

        TEST_WINDOWING_COMPUTATION = False

        if (TEST_WINDOWING_COMPUTATION):
            # display and record to a file all events found, checking with rolling idA from None to 4. Save nbEvent and total len
            eventTimeLineList = []
            eventList = getAllEvents(connection)
            file = open("outEvent" + str(windowT) + ".txt", "w")
            file.write("Event name\nnb event\ntotal duration")
            for eventName in eventList:
                for animal in range(0, 5):
                    idA = animal
                    if idA == 0:
                        idA = None
                    timeLine = EventTimeLineCached(connection, file, eventName, idA, minFrame=minT, maxFrame=maxT)
                    eventTimeLineList.append(timeLine)
                    file.write(timeLine.eventNameWithId + "\t" + str(len(timeLine.eventList)) + "\t" + str(
                        timeLine.getTotalLength()) + "\n")
            file.close()
        flushEventTimeLineCache()

    except:

        exc_type, exc_value, exc_traceback = sys.exc_info()
        lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        error = ''.join('!! ' + line for line in lines)

        t = TaskLogger(connection)
        t.addLog(error)
        flushEventTimeLineCache()

        raise FileProcessException()

def insertNightEventWithInputs(file, startNightInput, endNightInput):
    '''
    This function create night event
    '''

    connection = sqlite3.connect(file)

    nightTimeLine = EventTimeLine(connection, "night", None, None, None, None)

    flushNightEvents(connection)

    nightTimeLineFlushed = EventTimeLine(connection, "night", None, None, None, None)

    try:
        startNight = datetime.time(int(startNightInput.split(":")[0]), int(startNightInput.split(":")[1]),
                                   int(startNightInput.split(":")[2]))
    except ValueError:
        raise ValueError("Incorrect time format, should be hh:mm:ss")

    try:
        endNight = datetime.time(int(endNightInput.split(":")[0]), int(endNightInput.split(":")[1]),
                                 int(endNightInput.split(":")[2]))
    except ValueError:
        raise ValueError("Incorrect time format, should be hh:mm:ss")

    """
    Two cases: 
    - end night hour < start night hour means end night hour is the day after
    - end night hour > start night hour means the night is during the day: reverse cycle
    """

    if (endNight < startNight):
        cycle = "normal"
    else:
        cycle = "reverse"

    currentNight = Night(startHour=startNight, endHour=endNight, cycle=cycle)

    '''Beginning and end of the experiment'''
    startExperimentDate = getStartInDatetime(file)

    endExperimentDate = getEndInDatetime(file)

    currentDay = datetime.datetime.strftime(startExperimentDate, "%Y-%m-%d")
    currentDay = datetime.datetime(int(currentDay.split("-")[0]), int(currentDay.split("-")[1]),
                                   int(currentDay.split("-")[2]))
    previousDay = currentDay - datetime.timedelta(days=1)
    previousDay = datetime.datetime.strftime(previousDay, "%Y-%m-%d")

    currentStartNightDate = datetime.datetime.strptime("%s %s" % (previousDay, startNight), "%Y-%m-%d %H:%M:%S")

    lastFrame = getNumberOfFrames(file)

    currentNight.setStartEndDate(currentStartNightDate)

    while (True):
        if (currentNight.startDate > endExperimentDate):
            break

        tmpStartFrame = recoverFrame(file, str(currentNight.startDate))
        tmpEndFrame = recoverFrame(file, str(currentNight.endDate))

        if ((tmpStartFrame == 0) & (tmpEndFrame == 0)):
            if ((currentNight.startDate < startExperimentDate) & (currentNight.endDate > endExperimentDate)):
                tmpStartFrame = 1
                tmpEndFrame = lastFrame
                nightTimeLineFlushed.addEvent(Event(tmpStartFrame, tmpEndFrame))
                nightTimeLineFlushed.endRebuildEventTimeLine(connection, deleteExistingEvent=True)
            else:
                '''night outside the experiment'''
                pass
        else:
            if (tmpStartFrame == 0):
                tmpStartFrame = 1

            if (tmpEndFrame == 0):
                tmpEndFrame = lastFrame

            nightTimeLineFlushed.addEvent(Event(tmpStartFrame, tmpEndFrame))
            nightTimeLineFlushed.endRebuildEventTimeLine(connection, deleteExistingEvent=True)

        '''next day'''
        currentNight.nextDay()

def NightInputs():
    print("Construction of night events")
    night = input("Do you want to rebuild the night ? Yes (Y) or No (N) :")
    startNightInput = input("Time of the beginning of the night (hh:mm:ss):")
    endNightInput = input("Time of the end of the night (hh:mm:ss):")

    return night, startNightInput, endNightInput

def CreateNights(file, night, startNightInput, endNightInput):
    if (night == "Y") or (night == "Yes") or (night == "Ye") or (night == "Da") or (night == "Oui") or (night == "Si"):
        print(f"Code launched for file {file}")
        connection = sqlite3.connect(file)
        flushNightEvents(connection)
        insertNightEventWithInputs(file, startNightInput, endNightInput)
        print("*** NIGHTS CREATED ***")
    else:
        print("THE NIGHTS WILL NOT BE BUILD !!!!")

# --------------------------------------------------------------------------------------------------------
# End of rebuild
# --------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------
# Start of export
# --------------------------------------------------------------------------------------------------------
def computeBehaviorsData(behavior, show=False):
    """ Computes the details (Mean, Nb, Std, CI95...) of behaviors."""

    name = behavior.eventName
    # nameAndIds = behavior.eventNameWithId
    idA = behavior.idA
    idB = behavior.idB
    idC = behavior.idC
    idD = behavior.idD
    totalLength = behavior.getTotalLength()
    meanLength = behavior.getMeanEventLength()
    numberOfEvents = behavior.getNumberOfEvent()
    stdLength = behavior.getStandardDeviationEventLength()

    """    if behavior.getMedianEventLength() is not None:
        medianLength = behavior.getMedianEventLength()
    else:
        medianLength = None"""

    medianLength = None

    CI95 = [None]*2
    if meanLength is not None:
        CI = 1.96 * behavior.getStandardDeviationEventLength() / np.math.sqrt(behavior.getNumberOfEvent())
        CI95[0] = meanLength - CI
        CI95[1] = meanLength + CI
    else:
        meanLength = None

    returnedBehaviors = {
        "name": name,
        "idA": idA,
        "idB": idB,
        "idC": idC,
        "idD": idD,
        "totalLength": totalLength,
        "meanLength": meanLength,
        "medianLength": medianLength,
        "numberOfEvents": numberOfEvents,
        "stdLength": stdLength,
        "CI95_low": CI95[0],
        "CI95_up": CI95[1]
    }

    # print(f"{nameAndIds}")
    # print(f"   -TotalLength: {totalLength} frames.")
    # print(f"   -MeanEventLength: {meanLength}")
    # print(f"   -MedianEventLength: {medianLength}")
    # print(f"   -NumberOfEvent: {numberOfEvents}")
    # print(f"   -StandardDeviationEventLength: {stdLength}")
    # print(f"   -The confidence interval (95%) is [{CI95[0]},{CI95[1]}].")

    # if show:
        # beh.plotEventDurationDistributionHist(nbBin=30, title="Timebin #"+str(bin) + " / " + beh.eventNameWithId)
        # beh.plotEventDurationDistributionBar(title="Timebin #"+str(bin) + " / " + beh.eventNameWithId)

    # TODO: Show the histogram of events, with a 'show' parameter, with one subplot per behavior

    return returnedBehaviors

def RebuildInputs():

    # Questions for the rebuild of the databases
    buildEvents = input("Do you want to rebuild the Events ?")
    # Questions for the creation of the csv files
    timeBinsDuration = int(input("Enter the TIMEBIN for ALL the files (1min =  1800 frames / 1h = 108000 frames): "))
    useNights = input("Do you want to use the Nights from the .sqlite files to computes the data ? ('Yes'/'No'): ")

    return buildEvents, timeBinsDuration, useNights

def Rebuild(file, files, buildEvents):

    global timeBinsDuration
    global useNights

    print("Processing file, please wait...")

    chronoFullBatch = Chronometer("Full batch")

    fileCount = 0  # File Counter
    if files != None:
        if fileCount == 0:  # First file
            try:
                fileCount += 1  # Increment file Counter
                if buildEvents == "Yes" or buildEvents == 'Y' or buildEvents == "yes":
                    process(file)
            except FileProcessException:
                print("STOP PROCESSING FILE " + file, file=sys.stderr)
        else:  # For other files than the first one
            try:
                process(file)
            except FileProcessException:
                print("STOP PROCESSING FILE " + file, file=sys.stderr)

def Export(count:int, file, files, timeBinsDuration, useNights):

    filenames = [os.path.basename(files[x]) for x in range(0, len(files))]

    ### DEFINE CONSTANTS ###
    start = {}
    stop = {}

    # Create a Global Dataframe with all data:
    dfGlobal = pd.DataFrame()

    fileName = filenames[count]

    # Check that 'filename' and the current file are the same
    # TODO CAN BE IMPROVED by extracting from the current file

    connection = sqlite3.connect(file)  # connect to database
    animalPool = AnimalPool()  # create an animalPool, which basically contains your animals
    animalPool.loadAnimals(connection)  # load infos about the animals

    animalNumber = animalPool.getNbAnimals()

    if useNights.lower() == "yes" or useNights.lower() == "y":
        NightFrames = animalPool.getNightStartStop()

        # TODO find number of night and create bins for each

        nbTimebin = []

        startFrame = NightFrames[0][0]
        stopFrame = NightFrames[0][1]

        nbTimebin.append(int((stopFrame - startFrame) / timeBinsDuration) + 1)

        nbTimebins = int((stopFrame - startFrame) / timeBinsDuration) + 1

        for filename in filenames:
            start[filename] = startFrame
            stop[filename] = stopFrame

    if useNights.lower() == "no" or useNights.lower() == "no":
        print("You should use the nights")

    # TODO Flush ALL the events !!

    # Different events Depending on the number of animals in the Database:
    if animalNumber >= 1:
        behavioralEventsForOneAnimal = ["Move", "Move isolated", "Rearing", "Rear isolated",
                                        "Stop isolated", "WallJump", "SAP", "Huddling", "WaterPoint", "Distance"]
        # print("The behaviors extracted are:\n", behavioralEventsForOneAnimal)
    if animalNumber >= 2:
        behavioralEventsForTwoAnimals = ["Contact", "Oral-oral Contact", "Oral-genital Contact",
                                         "Side by side Contact",
                                         "Side by side Contact, opposite way", "Social approach", "Social escape",
                                         "Approach contact", "Approach rear", "Break contact", "Get away",
                                         "FollowZone Isolated",
                                         "Train2", "Group2", "Move in contact", "Rear in contact"]
        # print("and:\n", behavioralEventsForTwoAnimals)
    if animalNumber >= 3:
        behavioralEventsForThreeAnimals = ["Group3", "Group 3 break", "Group 3 make"]
        # print("and:\n", behavioralEventsForThreeAnimals)
    if animalNumber >= 4:
        behavioralEventsForFourAnimals = ["Group4", "Group 4 break", "Group 4 make", "Nest3", "Nest4"]
        # print("and:", behavioralEventsForFourAnimals)

    # Export the Infos (Mean, Std, ...) of the Behaviors for each timebin:
    dicoOfBehInfos = {
        "Filename": None,
        "Date": None,
        "Cage": None,
        "Injection": None,
        "Night-Phase": None,
        "Bin": None,
        "start_frame": None,
        "stop_frame": None,
        "name": None,
        "idA": None,
        "idB": None,
        "idC": None,
        "idD": None,
        "RFidA": None,
        "RFidB": None,
        "RFidC": None,
        "RFidD": None,
        "GenoA": None,
        "GenoB": None,
        "GenoC": None,
        "GenoD": None,
        "totalLength": None,
        "meanLength": None,
        "medianLength": None,
        "numberOfEvents": None,
        "stdLength": None,
        "CI95_low": None,
        "CI95_up": None
    }

    dfOfBehInfos = pd.DataFrame()  # Dataframe with the details of the previous dict

    allBehaviorsInfo = {}

    # TODO one for loop on Nights and One for loop for the times bins inside the night
    night_count = 1
    for night in NightFrames:
        bin = 1
        bin_progress = tqdm(range(1, nbTimebins + 1), desc=f"Night {night_count} - Bins", position=0, leave=True)
        for z in bin_progress:
            startBin = (start[fileName] + (z - 1) * timeBinsDuration) + (night_count - 1) * (108000 * 24)
            stopBin = startBin + timeBinsDuration
            bin_progress.set_postfix(Bin=f"{bin}/{nbTimebins}")
            animalPool.loadDetection(start=startBin, end=stopBin)  # load the detection for the different bins

            # Update the dictionary with Start; Stop; and bin info:
            dicoOfBehInfos["start_frame"] = startBin
            dicoOfBehInfos["stop_frame"] = stopBin
            dicoOfBehInfos["Bin"] = bin
            dicoOfBehInfos["Night-Phase"] = night_count

            # Update the dictionary with Filename; Date; Cage; and Session info
            # Example file name "191104_Magel2_Cage4_LMT3_4mo - Copy.sqlite"
            dicoOfBehInfos["Filename"] = fileName[:-7]  # Remove the " - Copy.sqlite" part
            date, Xp, cage, Injection = fileName[:-7].split("_")  # Splits the name at '_'
            dicoOfBehInfos["Date"] = date
            dicoOfBehInfos["Cage"] = cage
            dicoOfBehInfos["Injection"] = Injection

            #### For 1+ ANIMAL ####
            if animalNumber >= 1:
                for behavior in behavioralEventsForOneAnimal:
                    for a in animalPool.getAnimalDictionnary():
                        if behavior == "Distance":
                            dist_temp = animalPool.getAnimalWithId(a).getDistance(startBin, stopBin)
                            dicoOfBehInfos.update({"name": "Distance", "totalLength": dist_temp,
                                                   "RFidA": animalPool.getAnimalWithId(a).RFID,
                                                   "GenoA": animalPool.getAnimalWithId(a).genotype,
                                                   "idA": a})
                        else:

                            eventTimeLine = EventTimeLine(connection, behavior, idA=a, minFrame=startBin,
                                                          maxFrame=stopBin)

                            behavioralDataOne = computeBehaviorsData(eventTimeLine)  # Computes the Stats.
                            dicoOfBehInfos.update(behavioralDataOne)  # ADD THE CALCULATIONS FROM THE EVENTIMELINE
                            dicoOfBehInfos.update({"RFidA": animalPool.getAnimalWithId(a).RFID,
                                                   "GenoA": animalPool.getAnimalWithId(a).genotype})

                        # Creates a dataFrame with the behavioral Infos from the dictionary:
                        index = [0]
                        dfOfBehInfosTemp = pd.DataFrame(dicoOfBehInfos, index=index)
                        dfOfBehInfos = dfOfBehInfos.append(dfOfBehInfosTemp, ignore_index=True)

                    # TODO for each Timebin, Plot the timeline of the behaviors ?
                    # plotMultipleTimeLine(behavioralList, title=behavior+" / timebin #"+str(bin), minValue=start)

            #### FOR 2+ ANIMALS ####
            if animalNumber >= 2:
                for behavior in behavioralEventsForTwoAnimals:
                    # print("**** ", behavior, " ****")
                    behavioralList2 = []

                    for a in animalPool.getAnimalDictionnary():
                        if behavior == "Move in contact" or behavior == "Rear in contact":  # Just idA in those behaviors
                            eventTimeLine = EventTimeLine(connection, behavior, idA=a, minFrame=startBin,
                                                          maxFrame=stopBin)
                            continue
                        for b in animalPool.getAnimalDictionnary():
                            if a == b:
                                continue
                            eventTimeLine = EventTimeLine(connection, behavior, idA=a, idB=b,
                                                          minFrame=startBin, maxFrame=stopBin)

                            behavioralDataTwo = computeBehaviorsData(eventTimeLine)  # Computes the Stats.
                            dicoOfBehInfos.update(behavioralDataTwo)  # ADD THE CALCULATIONS FROM THE EVENTIMELINE
                            dicoOfBehInfos.update({"RFidA": animalPool.getAnimalWithId(a).RFID,
                                                   "RFidB": animalPool.getAnimalWithId(b).RFID,
                                                   "GenoA": animalPool.getAnimalWithId(a).genotype,
                                                   "GenoB": animalPool.getAnimalWithId(b).genotype})

                            # Creates a dataFrame with the behavioral Infos from the dictionary:
                            index = [0]
                            dfOfBehInfosTemp = pd.DataFrame(dicoOfBehInfos, index=index)
                            dfOfBehInfos = dfOfBehInfos.append(dfOfBehInfosTemp, ignore_index=True)

            #### FOR 3+ ANIMALS ####
            if animalNumber >= 3:
                for behavior in behavioralEventsForThreeAnimals:
                    for a in animalPool.getAnimalDictionnary():
                        # There is ONLY ONE animal making or braking a group of 3 or 4 mice
                        if behavior == "Group 3 make" or behavior == "Group 3 break":
                            eventTimeLine = EventTimeLine(connection, behavior, idA=a, minFrame=startBin,
                                                          maxFrame=stopBin)
                            continue
                        for b in animalPool.getAnimalDictionnary():
                            if a == b:
                                continue
                            for c in animalPool.getAnimalDictionnary():
                                if a == c or b == c:
                                    continue
                                eventTimeLine = EventTimeLine(connection, behavior, idA=a, idB=b, idC=c,
                                                              minFrame=startBin, maxFrame=stopBin)

                                behavioralDataThree = computeBehaviorsData(eventTimeLine)  # Computes the Stats.
                                dicoOfBehInfos.update(
                                    behavioralDataThree)  # ADD THE CALCULATIONS FROM THE EVENTIMELINE
                                dicoOfBehInfos.update({"RFidA": animalPool.getAnimalWithId(a).RFID,
                                                       "RFidB": animalPool.getAnimalWithId(b).RFID,
                                                       "RFidC": animalPool.getAnimalWithId(c).RFID,
                                                       "GenoA": animalPool.getAnimalWithId(a).genotype,
                                                       "GenoB": animalPool.getAnimalWithId(b).genotype,
                                                       "GenoC": animalPool.getAnimalWithId(c).genotype})

                                # Creates a dataFrame with the behavioral Infos from the dictionary:
                                index = [0]
                                dfOfBehInfosTemp = pd.DataFrame(dicoOfBehInfos, index=index)
                                dfOfBehInfos = dfOfBehInfos.append(dfOfBehInfosTemp, ignore_index=True)

            #### FOR 4 ANIMALS ####
            if animalNumber >= 4:
                for behavior in behavioralEventsForFourAnimals:
                    for a in animalPool.getAnimalDictionnary():
                        # There is ONLY ONE animal making or braking a group of 3 or 4 mice
                        if behavior == "Group 4 make" or behavior == "Group 4 break":
                            eventTimeLine = EventTimeLine(connection, behavior, idA=a,
                                                          minFrame=startBin, maxFrame=stopBin)
                            continue
                        for b in animalPool.getAnimalDictionnary():
                            if a == b:
                                continue
                            for c in animalPool.getAnimalDictionnary():
                                if a == c or b == c:
                                    continue
                                # There is ONLY THREE animals making a Nest3
                                if behavior == "Nest3":
                                    eventTimeLine = EventTimeLine(connection, behavior, idA=a, idB=b, idC=c,
                                                                  minFrame=startBin, maxFrame=stopBin)
                                    continue
                                for d in animalPool.getAnimalDictionnary():
                                    if a == d or b == d or c == d:
                                        continue
                                    eventTimeLine = EventTimeLine(connection, behavior, idA=a, idB=b, idC=c, idD=d,
                                                                  minFrame=startBin, maxFrame=stopBin)

                                    behavioralDataFour = computeBehaviorsData(eventTimeLine)
                                    dicoOfBehInfos.update(behavioralDataFour)
                                    dicoOfBehInfos.update({"RFidA": animalPool.getAnimalWithId(a).RFID,
                                                           "RFidB": animalPool.getAnimalWithId(b).RFID,
                                                           "RFidC": animalPool.getAnimalWithId(c).RFID,
                                                           "RFidD": animalPool.getAnimalWithId(d).RFID,
                                                           "GenoA": animalPool.getAnimalWithId(a).genotype,
                                                           "GenoB": animalPool.getAnimalWithId(b).genotype,
                                                           "GenoC": animalPool.getAnimalWithId(c).genotype,
                                                           "GenoD": animalPool.getAnimalWithId(d).genotype})

                                    # Creates a dataFrame with the behavioral Infos from the dictionary:
                                    index = [0]
                                    dfOfBehInfosTemp = pd.DataFrame(dicoOfBehInfos, index=index)
                                    dfOfBehInfos = dfOfBehInfos.append(dfOfBehInfosTemp, ignore_index=True)

            bin += 1
        night_count += 1
    # count += 1  # TODO REPLACE THIS COUNT BY A FOR LOOP ON FILES

    dfOfBehInfos.to_csv(f"{fileName}.csv")  # Export the current dataframe into a .csv
    print(f"{fileName}.csv File Created !")
    print("######################## Close Connection with Database ##########################")
    connection.close()

# --------------------------------------------------------------------------------------------------------
# End of export
# --------------------------------------------------------------------------------------------------------

# # Select databases to rebuild and create csv
#
# files = getFilesToProcess()
#
# # Questions for the rebuild of the databases
#
# buildEvents = input("Do you want to rebuild the Events ?")
#
# # Questions for the creation of the csv files
#
# timeBinsDuration = int(input("Enter the TIMEBIN for ALL the files (1min =  1800 frames / 1h = 108000 frames): "))
# useNights = input("Do you want to use the Nights from the .sqlite files to computes the data ? ('Yes'/'No'): ")
#
# count = 0
# print(files)
#
# for file in files:
#     rebuild(file, files, buildEvents, night, startNightInput, endNightInput)
#     Export(count, file, files, timeBinsDuration, useNights)
#     count += 1

