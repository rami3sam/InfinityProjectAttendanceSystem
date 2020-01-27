import re
import pickle
import os
from facenet_pytorch import InceptionResnetV1
import os
import torch
import PIL
from classes import *
from core_functions import *

logger = createLogger('infinity','log.txt',True)

#initializes MTCNN face detector,resnet,and loadStudentsFiles
faceDetector = MTCNNFaceDetector(device,False,True)
resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)

#if reset is true it will recompute embeddings for all photos

reset = False
if reset == True:
    students = dict()
else:
    students = loadStudents()

for (dirpath, dirnames, filenames) in os.walk("students_photos"):
    
    #regualar expression to assert its a direct subdirectory to exclude cropped versions
    regexp = ''.join([r'^',STUDENTS_PHOTOS_DIR,r'/\w*$'])
    if re.match(regexp,dirpath):
        for filename in filenames:
            #checking if the file is .jpg to exclude embeddings
            if re.match(r'.+\.jpg$' , filename):            
                imagePath = os.path.join(dirpath ,filename)           
                studentID = dirpath.split('/')[1]

                #checking if the students exists or we create a new student object           
                if students.get(studentID,None) is None:
                    students[studentID] = StudentFile(studentID)
                #if embeddings are calculated there is no need to calculate it again
                if not (imagePath in students[studentID].processedPhotos):
                    os.makedirs(os.path.join(dirpath ,'cropped') ,exist_ok=True)
                    logger.info('Detecting faces in  : {}'.format(imagePath))
                    image = PIL.Image.open(imagePath)
                    imagePathCropped = os.path.join(dirpath ,'cropped', filename)
                    boxes,aligned = faceDetector.detectFace(image,imagePathCropped)
                    
                    logger.info('Calculating embeddings for : {}'.format(imagePath))

                    embeddings = resnet(aligned.unsqueeze(0))
                    embeddings = Embeddings(filename,embeddings)
                    students[studentID].embeddingsList.append(embeddings)
                    students[studentID].processedPhotos.append(imagePath)
                    logger.info('Successfully done : {}\n'.format(imagePath))

#Write student objects to files                
for studentID in students.keys():
    studentFilePath = os.path.join(STUDENTS_PHOTOS_DIR,studentID,"student.dat")
    with open(studentFilePath, 'wb') as studentFile:
        pickle.dump(students[studentID],studentFile)
        logger.info('Done saving file: {}'.format(studentFilePath))
            