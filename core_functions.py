import PIL
import os
import pickle
import re
import numpy as np
import cv2
import torch
from facenet_pytorch import MTCNN
import logging
import pymongo
logger = logging.getLogger('infinity')
#checks if torch library can use gpu if not not it chooses cpu
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
logger.info('Running on device: {}'.format(device))

STUDENTS_PHOTOS_DIR = 'students_photos'
DETECTED_FACES_DIR = 'detected_faces'
dbClient = pymongo.MongoClient("mongodb://localhost:27017/")
studentsDB = dbClient["mydatabase"]

def loadStudents():

    students = dict()
    regexp = ''.join([r'^',STUDENTS_PHOTOS_DIR,r'/\w*$'])

    for (dirpath, _, _) in os.walk("students_photos"):
        if re.match(regexp,dirpath):
            studentFilePath = os.path.join(dirpath ,'student.dat')
            if os.path.exists(studentFilePath):
                with open(studentFilePath,'rb') as studentFile:       
                    student = pickle.load(studentFile)
                    students[student.name] = student
    return students

def drawOnFrame(faceNumber,frame,boundingBoxes,studentID):
    boundingBoxes = np.array(boundingBoxes,dtype='int')
    #calculating coordinates for the border rectangle 
    startingPoint = (boundingBoxes[faceNumber][0],boundingBoxes[faceNumber][1]) #x0 y0
    endingPoint = (boundingBoxes[faceNumber][2],boundingBoxes[faceNumber][3]) #x1 y1
    cv2.rectangle(frame,startingPoint,endingPoint,(0,0,255),2)  
    logger.info('face {} : coordinates {} , {}'.format(faceNumber,startingPoint,endingPoint))
    #calculating coordiantes for the label rectangle
    startingPoint = (boundingBoxes[faceNumber][0],boundingBoxes[faceNumber][3]) #x0 y1
    label_height = ((boundingBoxes[faceNumber][3] - boundingBoxes[faceNumber][1]) // 4)
    endingPoint = (boundingBoxes[faceNumber][2],boundingBoxes[faceNumber][3] + label_height) #x1 y1+h
    cv2.rectangle(frame,startingPoint,endingPoint,(0,0,255),-1) 

    #textOrigin starting bottom left point and a bottom margin
    textOrigin = (startingPoint[0] ,endingPoint[1] - label_height // 5) 
    fontscale = label_height /40 
    cv2.putText(frame,studentID,textOrigin,cv2.FONT_HERSHEY_COMPLEX,fontscale,(255,255,255),2)
   

    #caculate face embedding
def calculateEmbeddingsErrors(resnet,alignedFaces,students):
    #torch.stack method accepts python array not tuples 
    alignedFaces = [*alignedFaces]
    alignedFaces = torch.stack(alignedFaces).to(device)
    calculatedEmbeddings = resnet(alignedFaces).detach().cpu()

    minimumDistanceDict = dict()
    for studentName in students:
        distancesArray = []
        for embeddings in students[studentName].embeddingsList:
            distance = (calculatedEmbeddings - embeddings.embeddings).norm().item()
            distancesArray.append (distance)
        logger.info('{} distances are: {}'.format(studentName ,distancesArray))
        minimumDistance = min(distancesArray)  
        minimumDistanceDict[minimumDistance] = studentName
        logger.info('{} minimum  distance is : {}'.format(studentName , minimumDistance))
    minimumDistance = min(minimumDistanceDict.keys())
    closestStudentName = minimumDistanceDict.get(minimumDistance)
    closestStudentId = 0 #0 is placeholder
    logger.info(' student is likely to be: {} '.format(closestStudentName).center(80,'*'))
    logger.info(' least distance is: {} '.format(minimumDistance).center(80,'*'))

    return closestStudentId,closestStudentName

       

def createLogger(loggerName,logFilename,logToConsole):
    logger = logging.getLogger(loggerName)
    handler = logging.FileHandler(logFilename)
    logger.addHandler(handler)
    if logToConsole == True:
        consoleHandler = logging.StreamHandler()
        logger.addHandler(consoleHandler)
    logger.setLevel(logging.INFO)
    return logger