#/bin/python
import cv2
import os
import torch
import PIL
import json
import datetime
from core_functions import faceDetector,resnet,DETECTED_FACES_DIR,calculateEmbeddingsErrors,\
    drawOnFrame,loadStudents,processStudentsErrorsList,getStudentByID,getSettings,logger
import requests
from io import BytesIO
import numpy as np

recognizedStudentsLists = []
MAX_CAM_NO = 8
CAMERA_URL_TEMP = 'http://{}:{}/photo.jpg'
CAMERA_IP_ADDRESSES  = getSettings('cameraIPS',['127.0.0.1'])
CAM_COLORS = ['#FF0000' , '#00FF00','#0000FF','#FFF000','#000FFF','#FF00FF','#F0000F','#0FFFF0']

camerasNumber = len(CAMERA_IP_ADDRESSES)
cameraFrames = [None] * camerasNumber
facesErrorsList = [None] * camerasNumber
recognizedStudentsLists = [[]] * camerasNumber

def processCameraFrame(cameraID,image):   
    
    global recognizedStudentsLists

    try:
        students = loadStudents()
        facesErrorsList[cameraID] = []
        croppedImageFilepath = os.path.join(DETECTED_FACES_DIR,'face.jpg')
        boundingBoxes,detectedFaces = faceDetector.detectFace(image, croppedImageFilepath)
        
        #reverse colors in image from RGB to BGR
        r, g, b = image.split()
        image = PIL.Image.merge("RGB", (b, g, r))
        cameraFrame = np.asarray(image)
        
        if boundingBoxes is not None:
            for faceID in range(0,len(boundingBoxes)):
                faceErrorsList = calculateEmbeddingsErrors(cameraID,faceID,detectedFaces[faceID],students,resnet)
                facesErrorsList[cameraID].extend(faceErrorsList)
        recognizedStudentsLists[cameraID] = processStudentsErrorsList(facesErrorsList[cameraID])
        for recognizedStudent in recognizedStudentsLists[cameraID]:
            drawOnFrame(cameraFrame,recognizedStudent.faceID,recognizedStudent.studentID,boundingBoxes,CAM_COLORS[cameraID])
            #cv2.imwrite('cameraFrame.jpg',cameraFrame)
        
    except Exception as e:
        logger.info(e)
    return cameraFrame


def getProcessedFrame(cameraID):
    global recognizedStudentsLists
    try:
        IPAddressWithPort = CAMERA_IP_ADDRESSES[cameraID]
        if ':' in IPAddressWithPort:
            IPAddress,port = IPAddressWithPort.split(':')
        else:
            IPAddress,port = IPAddressWithPort,8080
        cameraURL = CAMERA_URL_TEMP.format(IPAddress,port)
        response = requests.get(cameraURL)
        image = PIL.Image.open(BytesIO(response.content))
    except Exception as e:
        logger.info(e)
        recognizedStudentsLists[cameraID] = []
        return None
    
    cameraFrame = processCameraFrame(cameraID,image)
    
    return cameraFrame


def getRecognizedStudents():
    studentsJsonList = dict()
    for recognizedStudentsList in recognizedStudentsLists:
        for recognizedStudent in recognizedStudentsList:
            if studentsJsonList.get(recognizedStudent.studentID,None) == None:
                recongizedStudentID = recognizedStudent.studentID
                student = getStudentByID(recongizedStudentID,False)
                studentsJsonList[student.ID] = dict()
                
                studentsJsonList[student.ID]['name'] = student.name
                studentsJsonList[student.ID]['cameraID'] = [recognizedStudent.cameraID]
                studentsJsonList[student.ID]['colorMarkers'] = [CAM_COLORS[recognizedStudent.cameraID]]
            else:
                studentsJsonList[student.ID]['cameraID'].append(recognizedStudent.cameraID)
                studentsJsonList[student.ID]['colorMarkers'].append(CAM_COLORS[recognizedStudent.cameraID])
    return json.dumps(studentsJsonList)

def recognitionThread():
    global facesErrorsList
    facesErrorsList = [[None]] * len(CAMERA_IP_ADDRESSES)

    cameraID = 0
    while True:
        cameraFrames[cameraID] = getProcessedFrame(cameraID)
        studentsJsonList = getRecognizedStudents()

        imageFilenameTemp = f'shared/cameraFrame{cameraID}~.jpg'
        imageFilename = f'shared/cameraFrame{cameraID}.jpg'

        studentsJsonListFNTemp = 'shared/studentsJsonList~.txt'
        studentsJsonListFN = 'shared/studentsJsonList.txt'
        if cameraFrames[cameraID] is not None:
            cv2.imwrite(imageFilenameTemp,cameraFrames[cameraID])
            os.rename(imageFilenameTemp,imageFilename)
        with open(studentsJsonListFNTemp,'w') as f:
            print(studentsJsonList , file=f)

        
        os.rename(studentsJsonListFNTemp,studentsJsonListFN)

        cameraID+=1
        if cameraID == len(CAMERA_IP_ADDRESSES):
            cameraID = 0
            facesErrorsList = [[None]] * len(CAMERA_IP_ADDRESSES)
            
if __name__ == '__main__':
    recognitionThread()



