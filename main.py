import cv2
import os
import torch
import PIL
import json
import datetime
from flask_cors import CORS
from core_functions import faceDetector,resnet,DETECTED_FACES_DIR,calculateEmbeddingsErrors,\
    drawOnFrame,loadStudents,processStudentsErrorsList,getStudentByID
from flask import Flask, render_template,Response
from PIL import Image
import requests
from io import BytesIO
import numpy as np
import threading

recognizedStudentsList = []
CAMERA_URL = 'http://192.168.43.1:8080/photo.jpg'

app = Flask(__name__)
app.secret_key = "INFINITY_APP"

def process():   
    global students
    global recognizedStudentsList


    students = loadStudents()
    facesErrorsList = []
    response = requests.get(CAMERA_URL)
    image = Image.open(BytesIO(response.content))
    croppedImageFilepath = os.path.join(DETECTED_FACES_DIR,'face.jpg')
    boundingBoxes,aligned = faceDetector.detectFace(image, croppedImageFilepath)

    b, g, r = image.split()
    image = Image.merge("RGB", (r, g, b))
    frame = np.asarray(image)

    if boundingBoxes is not None:
        for faceID in range(0,len(boundingBoxes)):
            faceErrorsList = calculateEmbeddingsErrors(resnet,aligned[faceID],students,faceID)
           
            facesErrorsList.extend(faceErrorsList)
    recognizedStudentsList = processStudentsErrorsList(facesErrorsList)
    for recognizedStudent in recognizedStudentsList:
        drawOnFrame(recognizedStudent.faceID,frame,boundingBoxes,recognizedStudent.studentID)
    return frame

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/classMonitor')
def classMonitor():
    return render_template('classMonitor.html')


def getFrame():
    frame = process()
    ret, jpeg = cv2.imencode('.jpg', frame)
    return jpeg.tobytes()

def video_stream():
    while True:     
        if frame != None:
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_viewer')
def video_viewer():
    return Response(video_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/recognized_students')
def recognized_students():
    jsonList = dict()
    for recognizedStudent in recognizedStudentsList:
        recongizedStudentID = recognizedStudent.studentID
        student = getStudentByID(recongizedStudentID,False)
        jsonList[student.ID] = student.name
    return Response(json.dumps(jsonList))
    
import deleteStudent
import studentsList
import editStudent
import addStudent

def cameraThread():
    global frame
    while True:
        frame = getFrame()


if __name__ == '__main__':
    cam = threading.Thread(target=cameraThread)
    cam.start()
    app.run(host='0.0.0.0', threaded=True)
    





