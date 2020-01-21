import cv2
import numpy as np
from facenet_pytorch import MTCNN, InceptionResnetV1
import os
import torch
import PIL
import time
import logging
import json
import core_functions
from flask import Flask, render_template, Response

recognized_students_list = dict()
recognized_students_list_buffer = dict()

logger = logging.getLogger('infinity')
handler = logging.FileHandler('log.txt')
logger.addHandler(handler)
logger.setLevel(logging.INFO)

#initialize MTCNN face detector
mtcnn = core_functions.initializeMTCNN(True,False)
#Initialize ResNet Inception Model
resnet = InceptionResnetV1(pretrained='vggface2').eval().to(core_functions.device)
#Load precalculated students embeddings
all_embeddings = core_functions.loadEmbeddings()
logger.info('loaded students: {}'.format([*all_embeddings.keys()]))
logger.info('*'*80)
capture = cv2.VideoCapture(2)
app = Flask(__name__)

def process():   
    global recognized_students_list_buffer
    global recognized_students_list
    recognized_students_list_buffer = dict()
    ret, frame = capture.read()
    image = PIL.Image.fromarray(frame)
    boxes,aligned = core_functions.detectFace(mtcnn,image,'detected_faces/face.jpg')
    if boxes is not None:
        for i in range(0,len(boxes)):
           
            id, student_name = core_functions.calculateEmbeddingsErrors(resnet,aligned,all_embeddings)
            
            core_functions.drawOnFrame(i,frame,boxes,'#{:04d}'.format(id))
            recognized_students_list_buffer[id] = student_name
    recognized_students_list = recognized_students_list_buffer
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

@app.route('/recognized_students')
def recognized_students():
    return Response(json.dumps(recognized_students_list))

@app.teardown_appcontext
def teardown(x):
    handler.flush()
    


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)



    
#clean up and free allocated resources

capture.release()


