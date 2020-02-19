#/bin/python
import cv2
import os
import torch
import json
import datetime
import time
import DatabaseClient
from DatabaseClient import MAX_CAM_NO
from flask import Flask, render_template,Response,request,make_response
import requests
import logging
import FaceRecognition
databaseClient = DatabaseClient.DatabaseClient()

app = Flask(__name__)
app.secret_key = "INFINITY_APP"

capture = cv2.VideoCapture(0)

@app.route('/')
def index():
    return render_template('index.html')

def getFrame():
    
    ret, frame = capture.read()
    ret, jpeg = cv2.imencode('.jpg', frame)
    return jpeg.tobytes()

@app.route('/photo.jpg')
def getPCCameraFrame():
    response = make_response(getFrame())
    response.headers['Content-Type'] = 'image/jpeg'
    return response

@app.route('/classMonitor')
def classMonitor():
    CAMERA_IP_ADDRESSES  = databaseClient.getSettings('cameraIPS',['127.0.0.1:5000'])
    CAM_COLORS = databaseClient.getCameraColors()
    CAM_NO = len(CAMERA_IP_ADDRESSES)
    return render_template('classMonitor.html',MAX_CAM_NO=MAX_CAM_NO,CAM_NO=CAM_NO,CAM_COLORS=CAM_COLORS)




@app.route('/video_viewer/<cameraID>')
def video_viewer(cameraID):
    with open(f'shared/CAM_{cameraID}.jpg','rb') as f:
        cameraFrame = f.read()
    response = make_response(cameraFrame)
    response.headers['Content-Type'] = 'image/jpeg'
    return response

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
    





