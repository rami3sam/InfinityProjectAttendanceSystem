import PIL
import os
import pickle
import re
import numpy as np
import cv2
import torch
from facenet_pytorch import MTCNN
import logging

logger = logging.getLogger('infinity')
#checks if torch library can use gpu if not not it chooses cpu
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
logger.info('Running on device: {}'.format(device))

STUDENTS_PHOTOS_DIR = 'students_photos'

def detectFace(mtcnn,image,filename):
    alignedFaces ,_ = mtcnn(image,return_prob=True,save_path=filename);
    boundingBoxes,probabilites = mtcnn.detect(image)
    if boundingBoxes is not None:
        logger.info('Faces detected: {} with probabilites: {} '
        .format(len(boundingBoxes) , probabilites))
    else:
        logger.info("no faces detected")
    return boundingBoxes,alignedFaces

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
def drawOnFrame(i,frame,boundingBoxes,studentID):
    boundingBoxes = np.array(boundingBoxes,dtype='int')
    #calculating coordinates for the border rectangle 
    startingPoint = (boundingBoxes[i][0],boundingBoxes[i][1]) #x0 y0
    endingPoint = (boundingBoxes[i][2],boundingBoxes[i][3]) #x1 y1
    cv2.rectangle(frame,startingPoint,endingPoint,(0,0,255),2)  
    logger.info('face {} : coordinates {} , {}'.format(i,startingPoint,endingPoint))
    #calculating coordiantes for the label rectangle
    startingPoint = (boundingBoxes[i][0],boundingBoxes[i][3]) #x0 y1
    label_height = ((boundingBoxes[i][3] - boundingBoxes[i][1]) // 4)
    endingPoint = (boundingBoxes[i][2],boundingBoxes[i][3] + label_height) #x1 y1+h
    cv2.rectangle(frame,startingPoint,endingPoint,(0,0,255),-1) 

    #textOrigin starting bottom left point and a bottom margin
    textOrigin = (startingPoint[0] ,endingPoint[1] - label_height // 5) 
    fontscale = label_height /40 
    cv2.putText(frame,studentID,textOrigin,cv2.FONT_HERSHEY_COMPLEX,fontscale,(255,255,255),2)
   

    #caculate face embedding
def calculateEmbeddingsErrors(resnet,alignedFaces,students):
    #torch.stack method accepts python array not tuples 
    alignedFaces = [i for i in alignedFaces]
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
    closestStudentID = 0 #0 is placeholder
    logger.info(' student is likely to be: {} '.format(closestStudentName).center(80,'*'))
    logger.info(' least distance is: {} '.format(minimumDistance).center(80,'*'))

    return closestStudentID,closestStudentName

def initializeMTCNN(keepAll,selectLargestFace):
    return MTCNN(
    image_size=160, margin=0, min_face_size=20,
    thresholds=[0.6, 0.7, 0.7], factor=0.709, post_process=True,
    device=device,select_largest=selectLargestFace,keep_all=keepAll)       

def createLogger(loggerName,logFilename,logToConsole):
    logger = logging.getLogger(loggerName)
    handler = logging.FileHandler(logFilename)
    logger.addHandler(handler)
    if logToConsole == True:
        consoleHandler = logging.StreamHandler()
        logger.addHandler(consoleHandler)
    logger.setLevel(logging.INFO)
    return logger