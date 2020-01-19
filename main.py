import cv2
import numpy as np
from facenet_pytorch import MTCNN, InceptionResnetV1
import os
import torch
import PIL

workers = 0 if os.name == 'nt' else 4
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
print('Running on device: {}'.format(device))

mtcnn = MTCNN(
        image_size=160, margin=0, min_face_size=20,
        thresholds=[0.6, 0.7, 0.7], factor=0.709, post_process=True,
        device=device,
        keep_all=True,
       
)

def detectFace(frame):
    frame_PIL = PIL.Image.fromarray(frame)
    boxes,prob = mtcnn.detect(frame_PIL)
    if boxes is not None:
         print('Faces detected: ',len(boxes) ,',with probabilities :' ,prob)
    else:
        print("no faces detected")
    return boxes

capture = cv2.VideoCapture(0)
while(True):
     
    ret, frame = capture.read()
  
     
    boxes = detectFace(frame)

    #draw a border around the faces
    if boxes is not None:

        for i in range(0,len(boxes)):
            boxes_int = np.array(boxes,dtype='int')
            startpoint = tuple(boxes_int[i][0:2]) #x0 y0
            endpoint = tuple(boxes_int[i][2:4]) #x1 y1
            cv2.rectangle(frame,startpoint,endpoint,(0,0,255),2)  
            print('face ' , i ,': coordinates',startpoint ,endpoint)

    cv2.imshow('Infinity Project', frame)
    if cv2.waitKey(1) == 27:
        break
capture.release()
cv2.destroyAllWindows()
