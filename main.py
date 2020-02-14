#/bin/python
import cv2
import os
import torch
import PIL
import json
import datetime
from flask_cors import CORS
import DatabaseClient
from flask import Flask, render_template,Response,request,make_response
from PIL import Image
import requests
from io import BytesIO
import numpy as np
import threading
import FaceRecognition
import multiprocessing

databaseClient = DatabaseClient.DatabaseClient()
recognizedStudents = []
MAX_CAM_NO = 8
cameraFrames = [None] * MAX_CAM_NO
CAMERA_IP_ADDRESSES  = databaseClient.getSettings('cameraIPS',['127.0.0.1:5000'])
CAM_COLORS = ['#FF0000' , '#00FF00','#0000FF','#FFF000','#000FFF','#FF00FF','#F0000F','#0FFFF0']
NO_OF_PROCESSES = 3
currentProcess = 0
recogntionProcesses = []
app = Flask(__name__)
app.secret_key = "INFINITY_APP"

@app.route('/')
def index():
    return render_template('index.html')

def getFrame():
    capture = cv2.VideoCapture(0)
    ret, frame = capture.read()
    capture.release()
    ret, jpeg = cv2.imencode('.jpg', frame)
    return jpeg.tobytes()

@app.route('/photo.jpg')
def getPCCameraFrame():
    response = make_response(getFrame())
    response.headers['Content-Type'] = 'image/jpeg'
    return response

@app.route('/classMonitor')
def classMonitor():
    CAM_NO = len(CAMERA_IP_ADDRESSES)
    return render_template('classMonitor.html',MAX_CAM_NO=MAX_CAM_NO,CAM_NO=CAM_NO,CAM_COLORS=CAM_COLORS)




def getProcessedFrame(cameraID):
    global currentProcess
    while True:
        with open(f'shared/CAM_{cameraID:02d}.jpg','rb') as f:
            cameraFrame = f.read()
   
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + cameraFrame + b'\r\n\r\n')

@app.route('/video_viewer/<int:cameraID>')
def video_viewer(cameraID):
    return Response(getProcessedFrame(cameraID),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/recognized_students')
def recognized_students():
    studentsJsonList = '{}'
    with open(f'shared/RECOGNIZED_STUDENTS.txt','r') as f:
            studentsJsonList = f.read()
    return studentsJsonList
    
import deleteStudent
import studentsList
import editStudent
import addStudent
import generalSettings

def recogntionProcess(processNumber):
    rec = FaceRecognition.FaceRecognizer(processNumber)
    print('using device : {}'.format(rec.device))
    while True:
        rec.recognize()


if __name__ == '__main__':
    for processNumber in range(NO_OF_PROCESSES):
        process = multiprocessing.Process(target=recogntionProcess,args=[processNumber])
        process.start()
        recogntionProcesses.append(process)
    app.run(host='0.0.0.0', threaded=True)
    





