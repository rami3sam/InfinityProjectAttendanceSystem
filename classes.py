from facenet_pytorch import MTCNN
import pickle
import logging
logger = logging.getLogger('infinity')

class Student:
    def __init__(self,student):
        self.ID = student['ID']
        self.processedPhotos = student['processedPhotos']
        self.name = student['name']
        self.admissionYear = student['admissionYear']
        self.collegeYear = student['collegeYear']
        self.major = student['major']
        self.lastImageIndex = student['lastImageIndex']
        embeddingsListBuffer=[]
        for embeddings in student['embeddingsList']:
            embeddingsListBuffer.append(pickle.loads(embeddings))
        self.embeddingsList = embeddingsListBuffer

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