import PIL
import os
import pickle
import re
import numpy as np
import cv2
import torch
from facenet_pytorch import MTCNN,InceptionResnetV1
import logging
import pymongo
from classes import *
STUDENTS_PHOTOS_DIR = 'students_photos'
DETECTED_FACES_DIR = 'detected_faces'
STUDENTS_COL = 'students'
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg'])

majors = ['Electronic Engineering' , 'Electrical Engineering','Mecahnical Engineering']
years = ['First Year' ,'Second Year','Third Year','Fourth Year','Fifth Year']

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def loadStudents():
    studentsBuffer = dict()
    students = appDatabase[STUDENTS_COL].find()
    for student in students:
        studentsBuffer[student['ID']] = Student(student)
        #print( studentsBuffer[student['ID']].ID)
    return studentsBuffer

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
def calculateEmbeddingsErrors(resnet,alignedFace,students):
    #torch.stack method accepts python array not tuples 
    alignedFace = [alignedFace]
    alignedFace = torch.stack(alignedFace).to(device)
    calculatedEmbeddings = resnet(alignedFace).detach().cpu()

    minimumDistanceDict = dict()
    for studentID in students:
        distancesArray = []
        for embeddings in students[studentID].embeddingsList:
            distance = (calculatedEmbeddings - embeddings.embeddings).norm().item()
            distancesArray.append (distance)
        logger.info('{} distances are: {}'.format(studentID ,distancesArray))
        if len(distancesArray) == 0:
            continue
            
        minimumDistance = min(distancesArray)  
        minimumDistanceDict[minimumDistance] = studentID
        logger.info('{} minimum  distance is : {}'.format(studentID , minimumDistance))
    
    if len(minimumDistanceDict) == 0:
        return 0,'No students in the database'
    minimumDistance = min(minimumDistanceDict.keys())
    closestStudentId = minimumDistanceDict.get(minimumDistance)
    closestStudentName = students[closestStudentId].name
    logger.info(' student is likely to be: {} '.format(closestStudentName).center(80,'*'))
    logger.info(' least distance is: {} '.format(minimumDistance).center(80,'*'))

    return int(closestStudentId),closestStudentName

       

def createLogger(loggerName,logFilename,logToConsole):
    logger = logging.getLogger(loggerName)
    handler = logging.FileHandler(logFilename)
    logger.addHandler(handler)
    if logToConsole == True:
        consoleHandler = logging.StreamHandler()
        logger.addHandler(consoleHandler)
    logger.setLevel(logging.INFO)
    return logger



if 'init' not in vars():
    capture = cv2.VideoCapture(0)
    logger = createLogger('infinity','log.txt',True)
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    #checks if torch library can use gpu if not not it chooses cpu
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    logger.info('Running on device: {}'.format(device))

    mongoClient = pymongo.MongoClient("mongodb://localhost:27017/")
    appDatabase = mongoClient["infinity"]
    
    #initialize MTCNN face detector
    faceDetector = MTCNNFaceDetector(device,True,True)
    #Initialize ResNet Inception Model
    resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)
    init = False