import cv2
import numpy as np
from facenet_pytorch import MTCNN, InceptionResnetV1
import os
import torch
import PIL

#tests the host operating system windows or not and sets workers value accordingly
workers = 0 if os.name == 'nt' else 4
#tests if torch library can use gpu if not not it chooses cpu
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
print('Running on device: {}'.format(device))

#initializes MTCNN face detector, we want MTCNN to detect more than one face => keep_all = True 
#

mtcnn = MTCNN(
        image_size=160, margin=0, min_face_size=20,
        thresholds=[0.6, 0.7, 0.7], factor=0.709, post_process=True,
        device=device,
        keep_all=True,
)

def detectFace(frame):
#mtcnn.detect method accept PIL Image arguement	
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

    #draw a red border around detected faces
    if boxes is not None:

        for i in range(0,len(boxes)):
            boxes_int = np.array(boxes,dtype='int')
            #calculating coordinates for the border rectangle 
            startpoint = (boxes_int[i][0],boxes_int[i][1]) #x0 y0
            endpoint = (boxes_int[i][2],boxes_int[i][3]) #x1 y1
            cv2.rectangle(frame,startpoint,endpoint,(0,0,255),2)  
            print('face ' , i ,': coordinates',startpoint ,endpoint)

            #calculating coordiantes for the label rectangle
            startpoint = (boxes_int[i][0],boxes_int[i][3]) #x0 y1
            label_height = ((boxes_int[i][3] - boxes_int[i][1]) // 4)
            endpoint = (boxes_int[i][2],boxes_int[i][3] + label_height) #x1 y1+h
            cv2.rectangle(frame,startpoint,endpoint,(0,0,255),-1) 

    cv2.imshow('Infinity Project', frame)
	#to break from main loop if user presses ESC
    if cv2.waitKey(1) == 27:
        break
#clean up and free allocated resources
capture.release()
cv2.destroyAllWindows()
