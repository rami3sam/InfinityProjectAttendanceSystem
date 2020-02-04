import re
import pickle
import os
import torch
import PIL
from classes import *
from core_functions import *

def calculateStudentEmbeddings(studentID):
    databaseQuery = {'ID':studentID}
    studentDirPath = os.path.join("students_photos",studentID)
    if checkForStudentExistence(studentID):
        student = getStudentByID(studentID,False)
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
                    logger.info('Detecting faces in  : {}'.format(imagePath))
                    image = PIL.Image.open(imagePath)
                    imagePathCropped = os.path.join(dirpath ,'cropped', filename)
                    boxes,aligned = faceDetectorSingle.detectFace(image,imagePathCropped)
                    
                    logger.info('Calculating embeddings for : {}'.format(imagePath))
                    if aligned is None:
                        logger.info('Couldn\'t find faces in  : {}\n'.format(imagePath))
                        continue
                   
                    embeddings = resnet(aligned.unsqueeze(0))
                    embeddings = Embeddings(filename,embeddings)
                    embeddings = pickle.dumps(embeddings)

                    embeddingsList.append(embeddings)
                    processedPhotos.append(filename)
 
                    logger.info('Successfully done : {}\n'.format(imagePath))
          
        appDatabase[STUDENTS_COL].update_one(databaseQuery , {'$set':{
            'embeddingsList':embeddingsList,
            'processedPhotos':processedPhotos
        }})
        break
