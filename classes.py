from facenet_pytorch import MTCNN
import pickle
import logging
logger = logging.getLogger('infinity')

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

class Embeddings:
    def __init__(self,filename='',embeddings=None):
        self.filename=filename
        self.embeddings=embeddings

class MTCNNFaceDetector:
    def __init__(self,device,keepAll,selectLargestFace):
        self.mtcnn = MTCNN(
        image_size=160, margin=0, min_face_size=20,
        thresholds=[0.6, 0.7, 0.7], factor=0.709, post_process=True,
        device=device,select_largest=selectLargestFace,keep_all=keepAll)

    def detectFace(self,image,croppedImageFilename):
        alignedFaces ,_ = self.mtcnn(image,return_prob=True,save_path=croppedImageFilename);
        boundingBoxes,probabilites = self.mtcnn.detect(image)
        if boundingBoxes is not None:
            logger.info('Faces detected: {} with probabilites: {} '
            .format(len(boundingBoxes) , probabilites))
        else:
            logger.info("no faces detected")
        return boundingBoxes,alignedFaces