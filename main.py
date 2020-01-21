import cv2
import numpy as np
from facenet_pytorch import MTCNN, InceptionResnetV1
import os
import torch
import PIL
import time
from common_functions import detectFace
from common_functions import loadEmbeddings
from common_functions import drawOnFrame
from common_functions import calculateEmbeddingsErrors
from flask import Flask, render_template, Response
#checks if torch library can use gpu if not not it chooses cpu
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
print('Running on device: {}'.format(device))
#initialize MTCNN face detector
mtcnn = MTCNN(
        image_size=160, margin=0, min_face_size=20,
        thresholds=[0.6, 0.7, 0.7], factor=0.709, post_process=True,
        device=device,
        keep_all=True,
)
#Initialize ResNet Inception Model
resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)
#Load precalculated students embeddings
all_embeddings = loadEmbeddings()
print('loaded students: ' , *all_embeddings.keys())
print('*'*80)
capture = cv2.VideoCapture(0)
app = Flask(__name__)

def process():    
    ret, frame = capture.read()
    image = PIL.Image.fromarray(frame)
    boxes,aligned = detectFace(mtcnn,image,'detected_faces/face.jpg')
    if boxes is not None:
        for i in range(0,len(boxes)):
            calculateEmbeddingsErrors(resnet,device,aligned,all_embeddings)
            drawOnFrame(i,frame,boxes,"#????")
    time.sleep(1/10) #1/fps
	#to break from main loop if user presses ESC
    return frame;

@app.route('/')
def index():
    return render_template('index.html')

def getFrame():
    frame = process()
    ret, jpeg = cv2.imencode('.jpg', frame)
    return jpeg.tobytes()

def video_stream():
    while True:    
        frame = getFrame()
        if frame != None:
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/video_viewer')
def video_viewer():
    return Response(video_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)


    
#clean up and free allocated resources

capture.release()



