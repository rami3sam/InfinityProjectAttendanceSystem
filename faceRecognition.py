#/bin/python
import cv2
import os
import torch
import PIL
import json
import datetime
import requests
from io import BytesIO
import numpy as np
import os
import pickle
import re
import numpy as np
from facenet_pytorch import InceptionResnetV1
from AppClasses import Student,MTCNNFaceDetector,RecognitionResult,Embeddings
import DatabaseClient
recognizedStudentsLists = []

MAX_CAM_NO = 8
CAMERA_URL_TEMP = 'http://{}:{}/photo.jpg'
THRESHOLD=0.9

def hexToRGB(hex):
    hex = hex.lstrip('#')
    hex = '{}{}{}'.format(hex[4:6],hex[2:4],hex[0:2])
    return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))


class FaceRecognizer:
    def __init__(self):
        self.databaseClient = DatabaseClient.DatabaseClient()
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        self.faceDetector = MTCNNFaceDetector(self.device,True,True)
        self.resnet = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)
        self.reload()

    def reload(self):
        self.students = self.databaseClient.loadStudents()
        self.CAMERA_IP_ADDRESSES  = self.databaseClient.getSettings('cameraIPS',['127.0.0.1'])
        self.CAM_COLORS = ['#FF0000' , '#00FF00','#0000FF','#FFF000','#000FFF','#FF00FF','#F0000F','#0FFFF0']
        self.camerasNumber = len(self.CAMERA_IP_ADDRESSES)
        self.cameraFrames = [None] * self.camerasNumber
        self.facesErrorsList = [None] * self.camerasNumber
        self.cameraRecognizedStudentLists = [[]] * self.camerasNumber
    
    def calculateExistingStudentsEmbeddings(self):
        for studentID in self.students:
            self.calculateStudentEmbeddings(studentID)

    def drawLabelsOnFrame(self,cameraFrame,faceID,studentID,boundingBoxes,color):
        color = hexToRGB(color)
        boundingBoxes = np.array(boundingBoxes,dtype='int')
        #calculating coordinates for the border rectangle 
        startingPoint = (boundingBoxes[faceID][0],boundingBoxes[faceID][1]) #x0 y0
        endingPoint = (boundingBoxes[faceID][2],boundingBoxes[faceID][3]) #x1 y1
        cv2.rectangle(cameraFrame,startingPoint,endingPoint,color,2)  
        #calculating coordiantes for the label rectangle
        startingPoint = (boundingBoxes[faceID][0],boundingBoxes[faceID][3]) #x0 y1
        label_height = ((boundingBoxes[faceID][3] - boundingBoxes[faceID][1]) // 4)
        endingPoint = (boundingBoxes[faceID][2],boundingBoxes[faceID][3] + label_height) #x1 y1+h
        cv2.rectangle(cameraFrame,startingPoint,endingPoint,color,-1) 
        #textOrigin starting bottom left point and a bottom margin
        textOrigin = (startingPoint[0] ,endingPoint[1] - label_height // 5) 
        fontscale = label_height /40 
        cv2.putText(cameraFrame,studentID,textOrigin,cv2.FONT_HERSHEY_COMPLEX,fontscale,(255,255,255),2)
        #caculate face embedding
    def calculateEmbeddingsErrors(self,cameraID ,faceID,detectedFace):
        detectedFace = torch.stack([detectedFace]).to(self.device)
        calculatedEmbeddings = self.resnet(detectedFace).detach().cpu()
        faceErrorsList = []
        for studentID in self.students:
            errorsList = []
            for embeddings in self.students[studentID].embeddingsList:
                error = (calculatedEmbeddings - embeddings.embeddings).norm().item()
                errorsList.append (error)
            if len(errorsList) == 0:
                continue  
            studentMinimumError = min(errorsList)        
            if studentMinimumError < THRESHOLD:
                results = RecognitionResult(cameraID,faceID,studentID,studentMinimumError)
                faceErrorsList.append(results)
        return faceErrorsList

    def processStudentErrorsList(self,studentErrorsList):
        studentErrorsList = sorted(studentErrorsList,key=lambda x: x.errorValue)
        recognizedStudentsList = []
        while len(studentErrorsList) != 0 :
            closestStudent = studentErrorsList[0]
            recognizedStudentsList.append(closestStudent)
            recognitionResultListTemp = []
            for recognitionResult in studentErrorsList:
                if recognitionResult.faceID != closestStudent.faceID:
                    recognitionResultListTemp.append(recognitionResult)
            studentErrorsList = recognitionResultListTemp
        return recognizedStudentsList


    def processCameraFrame(self,cameraID,image):  
        self.facesErrorsList[cameraID] = []
        croppedImageFilepath = os.path.join(DatabaseClient.DETECTED_FACES_DIR,'face.jpg')
        facesBoundingBoxes,detectedFaces = self.faceDetector.detectFace(image, croppedImageFilepath)
       
        #reverse colors in image from RGB to BGR
        r, g, b = image.split()
        image = PIL.Image.merge("RGB", (b, g, r))
        cameraFrame = np.asarray(image)
        
        if facesBoundingBoxes is not None:
            detectedStudentsNumber = len(facesBoundingBoxes)
            print('detected {} students',detectedStudentsNumber)
            for faceID in range(0,detectedStudentsNumber):

                faceErrorsList = self.calculateEmbeddingsErrors(cameraID,faceID,detectedFaces[faceID])
                self.facesErrorsList[cameraID].extend(faceErrorsList)
        else:
            print('no student was detected')
        self.cameraRecognizedStudentLists[cameraID] = self.processStudentErrorsList(self.facesErrorsList[cameraID])
        for recognizedStudent in self.cameraRecognizedStudentLists[cameraID]:
            self.drawLabelsOnFrame(cameraFrame,recognizedStudent.faceID,recognizedStudent.studentID,facesBoundingBoxes,self.CAM_COLORS[cameraID])
            
        return cameraFrame


    def getFrameFromCamera(self,cameraID):
        try:
            IPAddressWithPort = self.CAMERA_IP_ADDRESSES[cameraID]
            if ':' in IPAddressWithPort:
                IPAddress,port = IPAddressWithPort.split(':')
            else:
                IPAddress,port = IPAddressWithPort,8080
            cameraURL = CAMERA_URL_TEMP.format(IPAddress,port)
            response = requests.get(cameraURL)
            cameraFrame = PIL.Image.open(BytesIO(response.content))
        except requests.exceptions.RequestException as e:
            print('Couldn\'t connect to camera {:02d}'.format(cameraID))
            self.cameraRecognizedStudentLists[cameraID] = []
            return None
         
        return cameraFrame


    def getRecognizedStudentsJSON(self):
        studentsJsonList = dict()
        for recognizedStudentsList in self.cameraRecognizedStudentLists:
            for recognizedStudent in recognizedStudentsList:
                if studentsJsonList.get(recognizedStudent.studentID,None) == None:
                    recongizedStudentID = recognizedStudent.studentID
                    student = self.databaseClient.getStudentByID(recongizedStudentID,False)
                    studentsJsonList[student.ID] = dict()
                    
                    studentsJsonList[student.ID]['name'] = student.name
                    studentsJsonList[student.ID]['cameraID'] = [recognizedStudent.cameraID]
                    studentsJsonList[student.ID]['colorMarkers'] = [self.CAM_COLORS[recognizedStudent.cameraID]]
                else:
                    studentsJsonList[student.ID]['cameraID'].append(recognizedStudent.cameraID)
                    studentsJsonList[student.ID]['colorMarkers'].append(self.CAM_COLORS[recognizedStudent.cameraID])
        return json.dumps(studentsJsonList)



    def calculateStudentEmbeddings(self,studentID):
        
        studentDirPath = os.path.join("students_photos",studentID)
        if self.databaseClient.checkForStudentExistence(studentID):
            student = self.databaseClient.getStudentByID(studentID,False)
            embeddingsList = student.embeddingsList
            processedPhotos = student.processedPhotos
        else:
            return

        for (dirpath, dirnames, filenames) in os.walk(studentDirPath):
            #regualar expression to assert its a direct subdirectory to exclude cropped versions
            for filename in filenames:
                #checking if the file is .jpg to exclude embeddings
                if re.match(r'.+\.(jpg|jpeg)$' , filename):                    
                    #if embeddings are calculated there is no need to calculate it again
                
                    if  filename not in processedPhotos:
                        imagePath = os.path.join(studentDirPath,  filename)
                        os.makedirs(os.path.join(dirpath ,'cropped') ,exist_ok=True)
                        print('Detecting faces in  : {}'.format(imagePath))
                        image = PIL.Image.open(imagePath)
                        imagePathCropped = os.path.join(dirpath ,'cropped', filename)
                        boundingBoxes,detectedFace = self.faceDetector.detectFace(image,imagePathCropped)
                        
                        print('Calculating embeddings for : {}'.format(imagePath))
                        if detectedFace is None:
                            print('Couldn\'t find faces in  : {}\n'.format(imagePath))
                            continue
                    
                        detectedFace = torch.stack([detectedFace[0]]).to(self.device)
                        embeddings = self.resnet(detectedFace).detach().cpu()
                        embeddings = Embeddings(filename,embeddings)
                        embeddings = pickle.dumps(embeddings)

                        embeddingsList.append(embeddings)
                        processedPhotos.append(filename)
                        print('Successfully done : {}\n'.format(imagePath))
                      
            self.databaseClient.updateEmbeddings(studentID,embeddingsList,processedPhotos)
            break
    
    def recognize(self):
        cameraID = 0
        facesErrorsList = [[None]] * self.camerasNumber
        for _ in range(0,self.camerasNumber):
            for studentID in self.students:
                self.calculateStudentEmbeddings(studentID)

            cameraFrame = self.getFrameFromCamera(cameraID)
            if cameraFrame is None:
                continue

            self.cameraFrames[cameraID] = self.processCameraFrame(cameraID,cameraFrame)
            recognizedStudentsJSONList = self.getRecognizedStudentsJSON()

            imageFilenameTemp = f'shared/cameraFrame{cameraID}~.jpg'
            imageFilename = f'shared/cameraFrame{cameraID}.jpg'
            studentsJsonListFNTemp = 'shared/studentsJsonList~.txt'
            studentsJsonListFN = 'shared/studentsJsonList.txt'

            if self.cameraFrames[cameraID] is not None:
                cv2.imwrite(imageFilenameTemp,self.cameraFrames[cameraID])
                os.rename(imageFilenameTemp,imageFilename)

                with open(studentsJsonListFNTemp,'w') as f:
                    print(recognizedStudentsJSONList , file=f)
                os.rename(studentsJsonListFNTemp,studentsJsonListFN)

            cameraID+=1


if __name__ == '__main__':
    rec = FaceRecognizer()
    print('using device : {}'.format(rec.device))
    while True:
        rec.recognize()


