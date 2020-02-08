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

recognizedStudentsLists = []
MAX_CAM_NO = 8
CAMERA_URL_TEMP = 'http://{}:8080/photo.jpg'
CAMERA_IP_ADDRESSES = ['192.168.43.1','192.168.43.2']
CAM_COLORS = ['#FF0000' , '#00FF00','#0000FF','#FFF000','#000FFF','#FF00FF','#F0000F','#0FFFF0']
app = Flask(__name__)
app.secret_key = "INFINITY_APP"

def processCameraFrame(cameraID,image):   
    global students
    global recognizedStudentsLists
    global facesErrorsList
    students = loadStudents()
    facesErrorsList[cameraID] = []
    croppedImageFilepath = os.path.join(DETECTED_FACES_DIR,'face.jpg')
    boundingBoxes,alignedFaces = faceDetector.detectFace(image, croppedImageFilepath)

    b, g, r = image.split()
    image = Image.merge("RGB", (r, g, b))
    cameraFrame = np.asarray(image)

    if boundingBoxes is not None:
        for faceID in range(0,len(boundingBoxes)):
            faceErrorsList = calculateEmbeddingsErrors(cameraID,faceID,alignedFaces[faceID],students,resnet)
            facesErrorsList[cameraID].extend(faceErrorsList)
    recognizedStudentsLists[cameraID] = processStudentsErrorsList(facesErrorsList[cameraID])
    for recognizedStudent in recognizedStudentsLists[cameraID]:
        drawOnFrame(cameraFrame,recognizedStudent.faceID,recognizedStudent.studentID,boundingBoxes,CAM_COLORS[cameraID])
    return cameraFrame

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/classMonitor')
def classMonitor():
    CAM_NO = len(CAMERA_IP_ADDRESSES)
    return render_template('classMonitor.html',MAX_CAM_NO=MAX_CAM_NO,CAM_NO=CAM_NO,CAM_COLORS=CAM_COLORS)


def getProcessedFrame(cameraID):
    global recognizedStudentsLists
    try:
        cameraURL = CAMERA_URL_TEMP.format(CAMERA_IP_ADDRESSES[cameraID])
        response = requests.get(cameraURL)
        image = Image.open(BytesIO(response.content))
    except:
        recognizedStudentsLists[cameraID] = []
        return None

    cameraFrame = processCameraFrame(cameraID,image)
    ret, jpeg = cv2.imencode('.jpg', cameraFrame)
    return jpeg.tobytes()

def video_stream(cameraID):
    while True:     
        if cameraFrames[cameraID] != None:
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + cameraFrames[cameraID] + b'\r\n\r\n')

@app.route('/video_viewer/<int:cameraID>')
def video_viewer(cameraID):
    return Response(video_stream(cameraID),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/recognized_students')
def recognized_students():
    jsonList = dict()
    cameraID = 0
    for recognizedStudentsList in recognizedStudentsLists:
        for recognizedStudent in recognizedStudentsList:
            if jsonList.get(recognizedStudent.studentID,None) == None:
                recongizedStudentID = recognizedStudent.studentID
                student = getStudentByID(recongizedStudentID,False)
                jsonList[student.ID] = dict()
                
                jsonList[student.ID]['name'] = student.name
                jsonList[student.ID]['cameraID'] = [recognizedStudent.cameraID]
                jsonList[student.ID]['colorMarkers'] = [CAM_COLORS[recognizedStudent.cameraID]]
            else:
                jsonList[student.ID]['cameraID'].append(recognizedStudent.cameraID)
                jsonList[student.ID]['colorMarkers'].append(CAM_COLORS[recognizedStudent.cameraID])

    return Response(json.dumps(jsonList))
    
import deleteStudent
import studentsList
import editStudent
import addStudent

def cameraThread():
    global cameraFrames
    global facesErrorsList
    global recognizedStudentsLists
    camerasNumber = len(CAMERA_IP_ADDRESSES)
    cameraFrames = [None] * camerasNumber
    facesErrorsList = [None] * camerasNumber
    recognizedStudentsLists = [[]] * camerasNumber
    cameraID = 0
    while True:
        cameraFrames[cameraID] = getProcessedFrame(cameraID)
        cameraID+=1
        if cameraID == len(CAMERA_IP_ADDRESSES):
            cameraID = 0
            facesErrorsList = [[None]] * len(CAMERA_IP_ADDRESSES)


if __name__ == '__main__':
    cam = threading.Thread(target=cameraThread)
    cam.start()
    app.run(host='0.0.0.0', threaded=True)
    





