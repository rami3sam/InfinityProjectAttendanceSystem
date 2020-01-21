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

def detectFace(mtcnn,image,filename):
    aligned ,_ = mtcnn(image,return_prob=True,save_path=filename);
    boxes,prob = mtcnn.detect(image)
    if boxes is not None:
        logger.info('\nFaces detected: {} with probability: {} '.format(len(boxes) , prob))
    else:
        logger.info("no faces detected")
    return boxes,aligned

def loadEmbeddings():
    i = 0
    all_embeddings = dict()
    for (dirpath, dirnames, filenames) in os.walk("students_photos"):
        if re.match(r'^students_photos/\w*$',dirpath):
            embeddingsPath = os.path.join(dirpath ,'embeddings')
            with open(embeddingsPath,'rb') as embeddingsFile:
                i+=1
                student_id = dirpath.split('/')[1]
                student_embedding = pickle.load(embeddingsFile)
                all_embeddings[student_id] = dict(id=i,embeddings=student_embedding)
    return all_embeddings

def drawOnFrame(i,frame,boxes,student_id):
    boxes_int = np.array(boxes,dtype='int')
    #calculating coordinates for the border rectangle 
    startpoint = (boxes_int[i][0],boxes_int[i][1]) #x0 y0
    endpoint = (boxes_int[i][2],boxes_int[i][3]) #x1 y1
    cv2.rectangle(frame,startpoint,endpoint,(0,0,255),2)  
    logger.info('face {} : coordinates {} , {}'.format(i,startpoint,endpoint))
    #calculating coordiantes for the label rectangle
    startpoint = (boxes_int[i][0],boxes_int[i][3]) #x0 y1
    label_height = ((boxes_int[i][3] - boxes_int[i][1]) // 4)
    endpoint = (boxes_int[i][2],boxes_int[i][3] + label_height) #x1 y1+h
    cv2.rectangle(frame,startpoint,endpoint,(0,0,255),-1) 

    #textOrigin starting bottom left point and a bottom margin
    textOrigin = (startpoint[0] ,endpoint[1] - label_height // 5) 
    fontscale = label_height /40 
    cv2.putText(frame,student_id,textOrigin,cv2.FONT_HERSHEY_COMPLEX,fontscale,(255,255,255),2)
   

    #caculate face embedding
def calculateEmbeddingsErrors(resnet,aligned,all_embeddings):
    #torch.stack method accepts python array not tuples 
    aligned = [i for i in aligned]
    aligned = torch.stack(aligned).to(device)
    calculatedEmbeddings = resnet(aligned).detach().cpu()

    dist_dict = dict()
    for key in all_embeddings:
        dist_arr = []
        for embeddings in all_embeddings[key]['embeddings']:
            dist = (calculatedEmbeddings - embeddings).norm().item()
            dist_arr.append (dist)
        logger.info('{} distances are: {}'.format(key ,dist_arr))
        min_dist = min(dist_arr)  
        dist_dict[min_dist] = key
        logger.info('{} minimum  distance is : {}'.format(key , min_dist))
    min_dist = min(dist_dict.keys())
    nearest_student = dist_dict.get(min_dist)
    logger.info(' student is likely to be: {} '.format(nearest_student).center(80,'*'))
    logger.info(' least distance is: {} '.format(min_dist).center(80,'*'))
    return all_embeddings[nearest_student]['id'],nearest_student

def initializeMTCNN(keep_all,select_largest):
    return MTCNN(
    image_size=160, margin=0, min_face_size=20,
    thresholds=[0.6, 0.7, 0.7], factor=0.709, post_process=True,
    device=device,select_largest=select_largest,keep_all=keep_all)       