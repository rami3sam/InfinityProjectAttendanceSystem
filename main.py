import cv2
import numpy as np
from facenet_pytorch import InceptionResnetV1
import os
import torch
import PIL
import time
import logging
import json
from flask_cors import CORS
from core_functions import *

from classes import *
from flask import Flask, render_template, Response

recognizedStudentsList = dict()
recognizedStudentsListBuffer = dict()
logger = createLogger('infinity','log.txt',True)

#initialize MTCNN face detector
faceDetector = MTCNNFaceDetector(device,True,False)
#Initialize ResNet Inception Model
resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)
#Load precalculated students embeddings
students = loadStudents()
logger.info('loaded students: {}'.format([*students.keys()]))
logger.info('*'*80)
capture = cv2.VideoCapture(1)
app = Flask(__name__)
CORS(app)
#disable flask logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

def process():   
    global recognizedStudentsListBuffer
    global recognizedStudentsList
    recognizedStudentsListBuffer = dict()
    ret, frame = capture.read()
    image = PIL.Image.fromarray(frame)
    croppedImageFilepath = os.path.join(DETECTED_FACES_DIR,'face.jpg')
    boxes,aligned = faceDetector.detectFace(image, croppedImageFilepath)
    if boxes is not None:
        for i in range(0,len(boxes)):
           
            id, student_name = calculateEmbeddingsErrors(resnet,aligned,students)
            
            drawOnFrame(i,frame,boxes,'#{:04d}'.format(id))
            recognizedStudentsListBuffer[id] = student_name
    recognizedStudentsList = recognizedStudentsListBuffer
	#to break from main loop if user presses ESC
    return frame

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/addStudent')
def addstudetn():
    return render_template('addStudent.html')

def getFrame():
    frame = process()
    ret, jpeg = cv2.imencode('.jpg', frame)
    return jpeg.tobytes()

def video_stream():
    #Stopped the opencv part to focus on developing the webserver
    #Change to True if you want opencv output
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
    return Response(json.dumps(recognizedStudentsList))

@app.teardown_appcontext
def teardown(x):
    logging.shutdown()
    


if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)



    
#clean up and free allocated resources

capture.release()


