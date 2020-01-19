import cv2
import numpy as np
from facenet_pytorch import MTCNN, InceptionResnetV1
import os
import torch
import PIL
def detectFace(frame):
    workers = 0 if os.name == 'nt' else 4
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    print('Running on device: {}'.format(device))

    mtcnn = MTCNN(
        image_size=160, margin=0, min_face_size=20,
        thresholds=[0.6, 0.7, 0.7], factor=0.709, post_process=True,
        device=device,
        keep_all=True,
       
    )

    frame = PIL.Image.fromarray(frame)
    aligned=[]
    boxes,prob = mtcnn.detect(frame)
    if boxes is not None:
         print('Face detected',len(boxes))
    else:
        print("no faces detected")
 #       names.append(dataset.idx_to_class[y])



capture = cv2.VideoCapture(0)
while(True):
     
    ret, frame = capture.read()
    cv2.imshow('video', frame)
     
    detectFace(frame)

    if cv2.waitKey(1) == 27:
        break
capture.release()
cv2.destroyAllWindows()
