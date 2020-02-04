import cv2
import os
import torch
import PIL
import json
import datetime
from flask_cors import CORS
from core_functions import faceDetector,resnet,DETECTED_FACES_DIR,capture,calculateEmbeddingsErrors,drawOnFrame,loadStudents
from flask import Flask, render_template,Response
from PIL import Image
import requests
from io import BytesIO
import numpy as np

recognizedStudentsList = dict()
recognizedStudentsListBuffer = dict()

app = Flask(__name__)
app.secret_key = "INFINITY_APP"

def process():   
    global students
    global recognizedStudentsListBuffer
    global recognizedStudentsList
    recognizedStudentsListBuffer = dict()
    response = requests.get('http://192.168.43.1:8080/photo.jpg')
    image = Image.open(BytesIO(response.content))
    b, g, r = image.split()
    image = Image.merge("RGB", (r, g, b))
    frame = np.asarray(image)
    croppedImageFilepath = os.path.join(DETECTED_FACES_DIR,'face.jpg')
    boxes,aligned = faceDetector.detectFace(image, croppedImageFilepath)
    if boxes is not None:
        for i in range(0,len(boxes)):
            studentID, studentName = calculateEmbeddingsErrors(resnet,aligned[i],students)
            
            drawOnFrame(i,frame,boxes,'#{:04d}'.format(studentID))
            recognizedStudentsListBuffer[studentID] = studentName
    recognizedStudentsList = recognizedStudentsListBuffer
    return frame

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/classMonitor')
def classMonitor():
    global students
    students = loadStudents()
    return render_template('classMonitor.html')


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
    return Response(json.dumps(recognizedStudentsList))
    
import deleteStudent
import studentsList
import editStudent
import addStudent

if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
    



    
#clean up and free allocated resources




