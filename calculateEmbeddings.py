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
from common_functions import detectFace
#tests if torch library can use gpu if not not it chooses cpu
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
print('Running on device: {}'.format(device))

#initializes MTCNN face detector, we want MTCNN to detect more than one face => keep_all = True 
#

mtcnn = MTCNN(
        image_size=160, margin=0, min_face_size=20,
        thresholds=[0.6, 0.7, 0.7], factor=0.709, post_process=True,
        device=device,select_largest=True
)

resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)

all_embeddings = []

for (dirpath, dirnames, filenames) in os.walk("students_photos"):

    #regualar expression to assert its a direct subdirectory to exclude cropped versions
    if re.match(r'^students_photos/\w*$',dirpath):
        for filename in filenames:
            #checking if the file is .jpg to exclude embeddings
            if re.match(r'.*.jpg$' , filename):
                
                os.makedirs(os.path.join(dirpath ,'cropped') ,exist_ok=True) 
                fullpath = os.path.join(dirpath ,filename)
                image = PIL.Image.open(fullpath)
                fullpathCropped = os.path.join(dirpath ,'cropped', filename)
                boxes,aligned = detectFace(mtcnn,image,fullpathCropped)
                print('successfully done : {}'.format(fullpath))

                embeddings = resnet(aligned.unsqueeze(0))
                all_embeddings.append(embeddings)
                #print('embeddings: {}'.format(embeddings))
                embeddingsPath = os.path.join(dirpath,"embeddings")

                with open(embeddingsPath, 'wb') as embeddingsFile:
                    pickle.dump(all_embeddings,embeddingsFile)
            