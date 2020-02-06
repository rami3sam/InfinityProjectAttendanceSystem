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
THRESHOLD=0.9

majors = ['Electronic Engineering' , 'Electrical Engineering','Mecahnical Engineering']
years = ['First Year' ,'Second Year','Third Year','Fourth Year','Fifth Year']

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def loadStudents():
    studentsBuffer = dict()
    students = appDatabase[STUDENTS_COL].find()
    for student in students:
        studentsBuffer[student['ID']] = Student(student,True)
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
def calculateEmbeddingsErrors(resnet,alignedFace,students,faceNumber):
    #torch.stack method accepts python array not tuples 
    calculatedEmbeddings = resnet(alignedFace.unsqueeze(0))
    faceErrorsList = []
    for studentID in students:
        errorsList = []
        for embeddings in students[studentID].embeddingsList:
            error = (calculatedEmbeddings - embeddings.embeddings).norm().item()
            errorsList.append (error)
        if len(errorsList) == 0:
            continue         
        minimumError = min(errorsList)        
        if minimumError < THRESHOLD:
            results = RecognitionResult(faceNumber,studentID,minimumError)
            faceErrorsList.append(results)
    
    return faceErrorsList

def processStudentsErrorsList(recognitionResultsList):
    
    recognitionResultsList = sorted(recognitionResultsList,key=lambda x: x.errorValue)
    recognizedStudentsList = []
    while len(recognitionResultsList) != 0 :
        closestStudent = recognitionResultsList[0]
        recognizedStudentsList.append(closestStudent)
        print('recognizedStudentsList :{}'.format(recognizedStudentsList))
        recognitionResultListTemp = []
        for recognitionResult in recognitionResultsList:
            if recognitionResult.faceID != closestStudent.faceID:
                 recognitionResultListTemp.append(recognitionResult)
        recognitionResultsList = recognitionResultListTemp
    return recognizedStudentsList

def createLogger(loggerName,logFilename,logToConsole):
    logger = logging.getLogger(loggerName)
    handler = logging.FileHandler(logFilename)
    logger.addHandler(handler)
    if logToConsole == True:
        consoleHandler = logging.StreamHandler()
        logger.addHandler(consoleHandler)
    logger.setLevel(logging.INFO)
    return logger


def checkForStudentExistence(studentID):
    databaseQuery = {'ID':studentID}
    return appDatabase[STUDENTS_COL].count_documents(databaseQuery) > 0

def getStudentByID(studentID,decodeEmbeddings):
    databaseQuery = {'ID':studentID}
    return Student(appDatabase[STUDENTS_COL].find_one(databaseQuery),decodeEmbeddings)


if 'init' not in vars():
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
    faceDetectorSingle = MTCNNFaceDetector(device,False,True)
    #Initialize ResNet Inception Model
    resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)
    init = False