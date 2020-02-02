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
    if appDatabase[STUDENTS_COL].count_documents(databaseQuery) == 1:
        student = appDatabase[STUDENTS_COL].find_one(databaseQuery)
        embeddingsList = student['embeddingsList']
        processedPhotos = student['processedPhotos']
    else:
        return

    for (dirpath, dirnames, filenames) in os.walk(studentDirPath):
        #regualar expression to assert its a direct subdirectory to exclude cropped versions
        for filename in filenames:
            #checking if the file is .jpg to exclude embeddings
            if re.match(r'.+\.jpg$' , filename):                    
                #if embeddings are calculated there is no need to calculate it again
            
                if  filename not in processedPhotos:
                    imagePath = os.path.join(studentDirPath,  filename)
                    os.makedirs(os.path.join(dirpath ,'cropped') ,exist_ok=True)
                    logger.info('Detecting faces in  : {}'.format(imagePath))
                    image = PIL.Image.open(imagePath)
                    imagePathCropped = os.path.join(dirpath ,'cropped', filename)
                    boxes,aligned = faceDetector.detectFace(image,imagePathCropped)
                    
                    logger.info('Calculating embeddings for : {}'.format(imagePath))
                    if len(aligned) == 0:
                        logger.info('Couldn\'t find faces in  : {}\n'.format(imagePath))
                        continue
                   
                    alignedFaces = [aligned[0]]
                    alignedFaces = torch.stack(alignedFaces).to(device)
                    embeddings = resnet(alignedFaces).detach().cpu()


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
