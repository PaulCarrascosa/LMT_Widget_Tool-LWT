"""
Created on 20 August 2019 + update in 2020 by D. Huzard + updated in 2023 by Paul Carrascosa

@author: D. Huzard, P. Carrascosa
"""

"""
This code will extract all the behaviors into timebins and export it in .csv files.
The Goal is to then use an ipywidget tool, based on dataframes to compute Graphs and mixed model statistics.
"""

import sys
sys.path.insert(1, "../")

import sqlite3
import warnings
warnings.simplefilter(action='ignore')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime
import os

from lmtanalysis.Animal import AnimalPool
from lmtanalysis.Event import EventTimeLine, plotMultipleTimeLine
from lmtanalysis.FileUtil import getFilesToProcess
from lmtanalysis.Measure import *
from IPython.display import display
import ipywidgets as widgets

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

def Export():
    files = getFilesToProcess()
    # if len(files) == 0:
    #     print("NO FILE TO PROCESS !!!!!")
    # if len(files) >= 1:
    filenames = [os.path.basename(files[x]) for x in range(0, len(files))]
    # print(f"{files} => {filenames}")

    ### DEFINE CONSTANTS ###
    start = {}
    stop = {}

    timeBinsDuration = int(input("Enter the TIMEBIN for ALL the files (1min =  1800 frames / 1h = 108000 frames): "))

    # fileGlobal = input("Enter the filename for the .csv WITH ALL DATA INSIDE: ")

    useNights = input("Do you want to use the Nights from the .sqlite files to computes the data ? ('Yes'/'No'): ")

    """
    useSameStartStop = input("Do you want to use the same start & stop frames for all DBs ? ('Yes'/'No'): ")

    if useSameStartStop.lower() == "yes":
        startAll = int(input(f"Enter the Global STARTING frame:"))
        stopAll = int(input(f"Enter the Global ENDING frame:"))
        nbTimebins = int((stopAll - startAll) / timeBinsDuration)
        print(f"There are {nbTimebins} timebins of {timeBinsDuration} frames (= {timeBinsDuration / 30 / 60} "
              f"minutes) between frames: Start={startAll} and Stop={stopAll}.")
        for filename in filenames:
            start[filename] = startAll
            stop[filename] = stopAll

    if useSameStartStop.lower() == "no":
        for filename in filenames:
            start[filename] = int(input(f"Enter the STARTING frame for {filename}:"))
            stop[filename] = int(input(f"Enter the ENDING frame for {filename}:"))
            nbTimebins = int((stop[filename] - start[filename]) / timeBinsDuration)
            print(f"There are {nbTimebins} timebins of {timeBinsDuration} frames (= {timeBinsDuration/30/60} minutes) "
                  f"between frames: Start={start[filename]} and Stop={stop[filename]}.")
    """

    #Create a Global Dataframe with all data:
    dfGlobal = pd.DataFrame()

    count = 0
    for file in files:
        # print(f"The current Count is : {count}")
        # print(f"file: {file}")
        # print(f"File path: {file.title()}")
        fileName = filenames[count]
        # print(f"File name: {fileName}")

        #Check that 'filename' and the current file are the same
        #TODO CAN BE IMPROVED by extracting from the current file

        # if fileName in file:
        #     print("THE FILE NAME MATCHES! !")
        # else:
        #     print("!!! ERROR: FILE NAME DO NOT MATCH!!")

        connection = sqlite3.connect(file) # connect to database
        animalPool = AnimalPool() # create an animalPool, which basically contains your animals
        animalPool.loadAnimals(connection) # load infos about the animals

        animalNumber = animalPool.getNbAnimals()
        # print(f"There are {animalNumber} animals,")

        if useNights.lower() == "yes" or useNights.lower() == "y":
            # Le problème vient d'ici (fonction getNightStartStop) ? Est-ce que ça ne prendrait pas juste la première
            # nuit ? Faire une boucle if qui dit que si night_phase > 1 alors on prendra, à chaque night_count,
            # les données des frames suivantes comme getNightStartStop ne prend que le startframe et le endframe de
            # l'évènement night ?
            NightFrames = animalPool.getNightStartStop()
            # print("The night events are:")
            # print(NightFrames)
            #print(NightFrames[0])

            #TODO find number of night and create bins for each

            nbTimebin = []

            startFrame = NightFrames[0][0]
            stopFrame = NightFrames[0][1]

            nbTimebin.append(int((stopFrame - startFrame) / timeBinsDuration)+1)
            # print("There are "+str(nbTimebin)+" timebins.")
            #
            # print(startFrame)
            # print(stopFrame)

            # for night in NightFrames:
            #     print(night)

            # for night in NightFrames:
            #     print(night)
            #     print(night[0])
            #     print(night[1])

            nbTimebins = int((stopFrame - startFrame) / timeBinsDuration)+1

            # print(f"There are {nbTimebins} timebins of {timeBinsDuration} frames (= {timeBinsDuration / 30 / 60} "
            #       f"minutes) during the night (between frames {startFrame} and {stopFrame}.)")

            for filename in filenames:
                start[filename] = startFrame
                stop[filename] = stopFrame

        if useNights.lower() == "no" or useNights.lower() == "no":
            print("AAAAaaaahhh")

        #TODO Flush ALL the events !!

        #Different events Depending on the number of animals in the Database:
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

        #TODO one for loop on Nights and One for loop for the times bins inside the night
        night_count = 1
        # print(NightFrames)
        for night in NightFrames:
            # print("The night is ", night)
            # print("The night_ count is ", night_count)
            bin = 1
            # Je pense que le problème vient du fait que toutes les valeurs sont en rapport avec le premier start bin
            # du fichier, donc au lieu de passer au jour suivant, ça va recommencer par rapport au premier start
            # bin...Le problème doit aussi venir de "dicoOfBehInfos" vu que ce sont les valeurs de Night-Phase qui
            # sont utilisées
            for z in range(night[0], night[1], timeBinsDuration):
                # print("Z is ", z)
                startBin = (start[fileName] + (bin-1) * timeBinsDuration) + (night_count-1) * (108000*24)
                stopBin = startBin + timeBinsDuration
                # print(bin)
            # for bin in range(nbTimebins):

                print(f"************* Loading data for bin #{bin} *************")
                # now = datetime.datetime.now()
                # print("Current date and time : ")
                # print(now.strftime("%Y-%m-%d %H:%M:%S"))
                # print(f"*** Start frame = {startBin} // Stop frame = {stopBin} ***")
                animalPool.loadDetection(start=startBin, end=stopBin)  # load the detection for the different bins

                #Update the dictionary with Start; Stop; and bin info:
                dicoOfBehInfos["start_frame"] = startBin
                dicoOfBehInfos["stop_frame"] = stopBin
                dicoOfBehInfos["Bin"] = bin
                dicoOfBehInfos["Night-Phase"] = night_count

                #Update the dictionary with Filename; Date; Cage; and Session info
                # Example file name "191104_Magel2_Cage4_LMT3_4mo - Copy.sqlite"
                dicoOfBehInfos["Filename"] = fileName[:-7] #Remove the " - Copy.sqlite" part
                date, Xp, cage, Injection = fileName[:-7].split("_")  # Splits the name at '_'
                # print(f"{date} , {Xp}, {cage}, {Injection}")
                dicoOfBehInfos["Date"] = date
                dicoOfBehInfos["Cage"] = cage
                dicoOfBehInfos["Injection"] = Injection

                # print("****** General parameters of the animals ****** ")
                # for animal in animalPool.getAnimalList():
                    # print("**")
                    # print(f"Animal RFID: {animal.RFID} / Animal Id: {animal.baseId} / Animal name: {animal.name}")
                    # print(f"Animal genotype: {animal.genotype}")
                    # nbOfDetectionFrames = len(animal.detectionDictionnary.keys()) timeInSecond =
                    # nbOfDetectionFrames / 30  # 30 fps print("Detection time: ", timeInSecond, "seconds.") print(
                    # "Distance traveled in arena (cm): ", animal.getDistance(tmin=start, tmax=stop))  # distance
                    # traveled

                #### For 1+ ANIMAL ####
                if animalNumber >= 1:
                    for behavior in behavioralEventsForOneAnimal:
                        # print("**** ", behavior, " ****")
                        # behavioralList1 = []

                        for a in animalPool.getAnimalDictionnary():
                            if behavior == "Distance":
                                # print("DISTANCE COMPUTE !!!!!!!!!!")
                                dist_temp = animalPool.getAnimalWithId(a).getDistance(startBin, stopBin)
                                # print(dist_temp)
                                dicoOfBehInfos.update({"name": "Distance", "totalLength": dist_temp,
                                                       "RFidA": animalPool.getAnimalWithId(a).RFID,
                                                       "GenoA": animalPool.getAnimalWithId(a).genotype,
                                                       "idA": a})
                            else:

                                eventTimeLine = EventTimeLine(connection, behavior, idA=a, minFrame=startBin,
                                                              maxFrame=stopBin)

                                behavioralDataOne = computeBehaviorsData(eventTimeLine) #Computes the Stats.
                                dicoOfBehInfos.update(behavioralDataOne) #ADD THE CALCULATIONS FROM THE EVENTIMELINE
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
                                eventTimeLine = EventTimeLine(connection, behavior, idA=a, minFrame=startBin, maxFrame=stopBin)
                                continue
                            for b in animalPool.getAnimalDictionnary():
                                if a == b:
                                    continue
                                eventTimeLine = EventTimeLine(connection, behavior, idA=a, idB=b,
                                                              minFrame=startBin, maxFrame=stopBin)

                                behavioralDataTwo = computeBehaviorsData(eventTimeLine)  #Computes the Stats.
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
                        # print("**** ", behavior, " ****")

                        for a in animalPool.getAnimalDictionnary():
                            # There is ONLY ONE animal making or braking a group of 3 or 4 mice
                            if behavior == "Group 3 make" or behavior == "Group 3 break":
                                eventTimeLine = EventTimeLine(connection, behavior, idA=a, minFrame=startBin, maxFrame=stopBin)
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
                                    dicoOfBehInfos.update(behavioralDataThree)  # ADD THE CALCULATIONS FROM THE EVENTIMELINE
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
                        # print("**** ", behavior, " ****")

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
        count += 1 # TODO REPLACE THIS COUNT BY A FOR LOOP ON FILES

        dfGlobal = dfGlobal.append(dfOfBehInfos)  # Add the data to the global Dataframe

        dfOfBehInfos.to_csv(f"{fileName}.csv") # Export the current dataframe into a .csv
        print(f"{fileName}.csv File Created !")
        print("##################################################################################")
        print("##################################################################################")
        print("######################## Close Connection with Database ##########################")
    connection.close()

    # dfGlobal.to_csv(f"{fileGlobal}.csv")  # Export the Global dataframe into a .csv
    # print(f"{fileGlobal}.csv File Created !")

    # Say it's done !
    print("!!! End of analysis !!!")

# if __name__ == '__main__':
#     Export()