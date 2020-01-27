import cv2
import numpy as np
from facenet_pytorch import InceptionResnetV1
import os
import torch
import PIL
import time
import logging
import json
import datetime
from flask_cors import CORS
from core_functions import *
from pymongo import *
from classes import *
from shutil import rmtree
from flask import Flask, render_template, Response,request,flash,redirect

recognizedStudentsList = dict()
recognizedStudentsListBuffer = dict()
logger = createLogger('infinity','log.txt',True)

ALLOWED_EXTENSIONS = set(['jpg', 'jpeg'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


#initialize MTCNN face detector
faceDetector = MTCNNFaceDetector(device,True,False)
#Initialize ResNet Inception Model
resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)
#Load precalculated students embeddings
students = loadStudents()
logger.info('loaded students: {}'.format([*students]))
logger.info('*'*80)
capture = cv2.VideoCapture(1)
app = Flask(__name__)
app.secret_key = "super secret key"

CORS(app)
#disable flask logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

majors = ['Electronic Engineering' , 'Electrical Engineering','Mecahnical Engineering']


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

@app.route('/addStudent',methods=['GET','POST'])
def addStudent():
    now = datetime.datetime.now() 
    if request.method == 'GET':
        
        return render_template('addStudent.html',now=now,majors=majors)
    elif request.method == 'POST':
        studentName = request.form.get('studentName')
        studentID = request.form.get('studentID')
        collegeYear = request.form.get('collegeYear')
        admissionYear = request.form.get('admissionYear')
        studentMajor = request.form.get('studentMajor')
        studentDict = dict(name=studentName,ID=studentID,
        collegeYear=collegeYear,admissionYear=admissionYear,major=studentMajor)
      
        
        if appDatabase[STUDENTS_COL].count_documents({'studentID':studentID},limit=1) > 0:
            flash('Student ID must be unique','error')
            return redirect(request.url)


        if 'images[]' not in request.files:
            flash('You must select at least one image','error')
            return redirect(request.url)
		
        images = request.files['images[]']
        if images.filename == '':
            flash('No images selected for uploading','error')
            return redirect(request.url)
        if images and allowed_file(images.filename):
            studentDir = os.path.join(STUDENTS_PHOTOS_DIR , studentID)
            os.makedirs(studentDir,exist_ok=True)
            for i,image in enumerate(request.files.getlist("images[]")):
                imageFilename = '{:04d}'.format(i)
                appDatabase[STUDENTS_COL].insert_one(studentDict)
                image.save(os.path.join(studentDir, imageFilename))
                flash('Student added successfully','success')
                return redirect('/addStudent')
        else:
            flash('Allowed file types are jpg, jpeg')
            return redirect(request.url)


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
    
@app.route('/studentsList')
def studentsList():
    students = appDatabase[STUDENTS_COL].find().skip(0).limit(10)
    return render_template('studentsList.html',students=students)

@app.route('/deleteStudent/<id>')
def deleteStudent(id):
    if appDatabase[STUDENTS_COL].count_documents({'ID':id}) > 0:
        appDatabase[STUDENTS_COL].remove({"ID":id})
        rmtree(os.path.join(STUDENTS_PHOTOS_DIR ,id),ignore_errors=True)
        return redirect('/studentsList')
    return(Respone('Invalid delete operation'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)



    
#clean up and free allocated resources

capture.release()


