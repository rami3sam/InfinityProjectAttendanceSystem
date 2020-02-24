#/bin/python
import cv2
import os
import json
import time
import DatabaseClient
from DatabaseClient import MAX_CAM_NO
from flask import Flask, render_template,Response,request,make_response
import logging
import FaceRecognition
import torch.multiprocessing as multiprocessing
import videoRecording
import threading
import argparse

databaseClient = DatabaseClient.DatabaseClient()



app = Flask(__name__)
app.secret_key = "INFINITY_APP"

capture = cv2.VideoCapture(0)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/photo.jpg')
def getPCCameraFrame():
    ret, frame = capture.read()
    if ret is True:
        ret, jpeg = cv2.imencode('.jpg', frame)
        imageBytes =  jpeg.tobytes()
        response = make_response(imageBytes)
        response.headers['Content-Type'] = 'image/jpeg'
        return response
    else:
        return ''

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
    studentsJsonList = databaseClient.loadDocument(DatabaseClient.SHARED_COL,'STUDENTS_JSON_LIST')
    if studentsJsonList is not None:
        del studentsJsonList['_id']
        del studentsJsonList['documentType']
        studentsJsonList = json.dumps(studentsJsonList)
        return studentsJsonList
    else:
        return '{}'

import deleteStudent
import studentsList
import editStudent
import addStudent
import generalSettings
import lecturesList
import addLecture
import deleteLecture
import editLecture
import lectureReview
def recogntionProcess(processNumber):
    rec = FaceRecognition.FaceRecognizer(processNumber)
    print('using device : {}'.format(rec.device))
    while True:
        rec.recognize()

def runServer():
    app.run(host='0.0.0.0', threaded=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Infinity Project Attendance System')
    parser.add_argument('-js' ,dest='just_server',action='store_true',help='just start the server')
    parser.add_argument('-df' ,dest='debug_flask',action='store_true',help='show flask debugging information')
    args = parser.parse_args()

    if args.debug_flask == False:
        logging.getLogger('werkzeug').disabled = True
        os.environ['WERKZEUG_RUN_MAIN'] = 'true'
    
    serverThread = threading.Thread(target=runServer)
    serverThread.start()
    time.sleep(5)
    print('flask server started. ')

    if args.just_server == False:
        for index in range(3):
            process = multiprocessing.Process(target=recogntionProcess,args=[index])
            process.start()
        time.sleep(5)

        videoRecording.startWritingVideo()
    
    
    





