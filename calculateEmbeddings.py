import re
import pickle
import os
import cv2
import numpy as np
from facenet_pytorch import MTCNN, InceptionResnetV1
import os
import torch
import PIL
import cv2
import core_functions
import logging
from classes import *
from core_functions import detectFace
#tests if torch library can use gpu if not not it chooses cpu
logger = core_functions.createLogger('infinity','log.txt',True)

device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
logger.info('Running on device: {}'.format(device))

#initializes MTCNN face detector,resnet,and loadStudentsFiles

mtcnn = core_functions.initializeMTCNN(False ,True)
resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)

reset = False
if reset == True:
    students = dict()
else:
    students = core_functions.loadStudents()

for (dirpath, dirnames, filenames) in os.walk("students_photos"):
    
    #regualar expression to assert its a direct subdirectory to exclude cropped versions
    regexp = ''.join([r'^',core_functions.STUDENTS_PHOTOS_DIR,r'/\w*$'])
    if re.match(regexp,dirpath):
        for filename in filenames:
            #checking if the file is .jpg to exclude embeddings
            if re.match(r'.*.jpg$' , filename):            
                imagePath = os.path.join(dirpath ,filename)           
                studentName = dirpath.split('/')[1]

                #checking if the students exists or we create a new student object           
                if students.get(studentName,None) is None:
                    students[studentName] = Student(studentName)
                #if embeddings are calculated there is no need to calculate it again
                if not (imagePath in students[studentName].processedPhotos):
                    os.makedirs(os.path.join(dirpath ,'cropped') ,exist_ok=True)
                    logger.info('Detecting faces in  : {}'.format(imagePath))
                    image = PIL.Image.open(imagePath)
                    imagePathCropped = os.path.join(dirpath ,'cropped', filename)
                    boxes,aligned = core_functions.detectFace(mtcnn,image,imagePathCropped)
                    
                    logger.info('Calculating embeddings for : {}'.format(imagePath))

                    embeddings = resnet(aligned.unsqueeze(0))
                    embeddings = Embeddings(filename,embeddings)
                    students[studentName].embeddingsList.append(embeddings)
                    students[studentName].processedPhotos.append(imagePath)
                    logger.info('Successfully done : {}\n'.format(imagePath))

               
for studentName in students.keys():
    studentFilePath = os.path.join(core_functions.STUDENTS_PHOTOS_DIR,studentName,"student.dat")
    with open(studentFilePath, 'wb') as studentFile:
        pickle.dump(students[studentName],studentFile)
        logger.info('Done saving file: {}'.format(studentFilePath))
            