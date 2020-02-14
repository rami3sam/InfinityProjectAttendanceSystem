from facenet_pytorch import MTCNN,extract_face,fixed_image_standardization
import pickle
import torch
import numpy as np
class Embeddings:
    def __init__(self,filename='',embeddings=None):
        self.filename=filename
        self.embeddings=embeddings

class Student:
    def __init__(self,student=None,decodeEmbeddings=False):
        if student is None:
            student = dict()

        self.ID = student.get('ID',-1)
        self.processedPhotos = student.get('processedPhotos',[])
        self.name = student.get('name','')
        self.admissionYear = student.get('admissionYear','')
        self.collegeYear = student.get('collegeYear','')
        self.major = student.get('major','')
        self.lastImageIndex = student.get('lastImageIndex',0)
        embeddingsListBuffer=[]
        
        for embeddings in student.get('embeddingsList',[]):
            if decodeEmbeddings == True:
                embeddingsListBuffer.append(pickle.loads(embeddings))
            else:
                embeddingsListBuffer.append(embeddings)
        self.embeddingsList = embeddingsListBuffer

    def getStudentAsDict(self):
        return dict(name=self.name,ID=self.ID,
        collegeYear=self.collegeYear,admissionYear=self.admissionYear,major=self.major,
        embeddingsList=self.embeddingsList,processedPhotos=self.processedPhotos,lastImageIndex=self.lastImageIndex)



class MTCNNFaceDetector:
    def __init__(self,device,keepAll,selectLargestFace):
        self.device = device
        self.mtcnn = MTCNN(
        image_size=160, margin=0, min_face_size=20,
        thresholds=[0.6, 0.7, 0.7], factor=0.709, post_process=True,
        device=device,select_largest=selectLargestFace,keep_all=keepAll)

    
    def detectFace(self,image,croppedImageFilename,multipleFaces=False):
        
        boundingBoxes,probabilites = self.mtcnn.detect(image)
        detectedFaces = []
        croppedImageFilename = ''.join(croppedImageFilename.split('.')[0:-1])
        if boundingBoxes is not None:
            if multipleFaces == False:
                maxProbIndex = np.argmax(probabilites)
                boundingBoxes=[boundingBoxes[maxProbIndex]]
            for index,boundingBox in enumerate(boundingBoxes):
              
                detectedFace = extract_face(image,boundingBox,160,0,'{}{}.jpg'.format(croppedImageFilename,index))
                detectedFace = fixed_image_standardization(detectedFace)
                detectedFaces.append(detectedFace)

        return boundingBoxes,detectedFaces

class RecognitionResult:
    def __init__(self,cameraID,faceID,studentID,errorValue):
        self.cameraID = cameraID
        self.faceID = faceID
        self.studentID = studentID
        self.errorValue = errorValue
