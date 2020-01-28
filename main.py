import cv2
import numpy as np
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
from calculateEmbeddings import *
recognizedStudentsList = dict()
recognizedStudentsListBuffer = dict()
logger = createLogger('infinity','log.txt',True)

students = loadStudents()

ALLOWED_EXTENSIONS = set(['jpg', 'jpeg'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

logger.info('*'*80)
capture = cv2.VideoCapture(0)
app = Flask(__name__)
app.secret_key = "super secret key"

CORS(app)
#disable flask logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

majors = ['Electronic Engineering' , 'Electrical Engineering','Mecahnical Engineering']
years = ['First Year' ,'Second Year','Third Year','Fourth Year','Fifth Year']

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
           
            studentID, studentName = calculateEmbeddingsErrors(resnet,aligned[i],students)
            
            drawOnFrame(i,frame,boxes,'#{:04d}'.format(studentID))
            recognizedStudentsListBuffer[studentID] = studentName
    recognizedStudentsList = recognizedStudentsListBuffer
	#to break from main loop if user presses ESC
    return frame

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/classMonitor')
def classMonitor():
    return render_template('classMonitor.html')

@app.route('/addStudent',methods=['GET','POST'])
def addStudent():
    global students
    now = datetime.datetime.now() 
    if request.method == 'GET':
        
        return render_template('addStudent.html',now=now,majors=majors,years=years)
    if request.method == 'POST':
        studentName = request.form.get('studentName')
        studentID = request.form.get('studentID')
        collegeYear = request.form.get('collegeYear')
        admissionYear = request.form.get('admissionYear')
        studentMajor = request.form.get('studentMajor')
        studentDict = dict(name=studentName,ID=studentID,
        collegeYear=collegeYear,admissionYear=admissionYear,major=studentMajor,
        embeddingsList=[],processedPhotos=[])
      
        
        if appDatabase[STUDENTS_COL].count_documents({'ID':studentID},limit=1) > 0:
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
                imagePath = '{}.{}'.format(os.path.join(studentDir, imageFilename),'jpg')
                image.save(imagePath)
                
        else:
            flash('Allowed file types are jpg, jpeg')
            return redirect(request.url)
        appDatabase[STUDENTS_COL].insert_one(studentDict)
        calculateStudentEmbeddings(studentID)
        students = loadStudents()
        flash('Student added successfully','success')
        return redirect('/addStudent')

@app.route('/editStudent/<studentID>',methods=['GET','POST'])
def editStudent(studentID):
    global students
    badEditOperation = Response('Invaid edit operation')
    now = datetime.datetime.now() 
    
    if request.method == 'GET':
            if appDatabase[STUDENTS_COL].count_documents({'ID':studentID}) > 0:
                student = students[studentID]
                return render_template('editStudent.html',now=now,majors=majors,
                years=years,student=student)
            else:
                return badEditOperation
   
    if request.method == 'POST':
        
        studentName = request.form.get('studentName')
        collegeYear = request.form.get('collegeYear')
        admissionYear = request.form.get('admissionYear')
        studentMajor = request.form.get('studentMajor')
        studentDict = dict(name=studentName,ID=studentID,
        collegeYear=collegeYear,admissionYear=admissionYear,major=studentMajor,
        embeddingsList=[],processedPhotos=[])

        if appDatabase[STUDENTS_COL].count_documents({'ID':studentID}) > 0:
            appDatabase[STUDENTS_COL].delete_many({'ID':studentID})
            appDatabase[STUDENTS_COL].insert_one(studentDict)
        
        images = request.files['images[]']
        if images and not images.filename == '':
            studentDir = os.path.join(STUDENTS_PHOTOS_DIR , studentID)
            lastIndex = 0
            os.makedirs(studentDir,exist_ok=True)
            for i in range(0,9999):
                filename = '{:04d}.jpg'.format(i)
                if os.path.exists(os.path.join(studentDir,filename)):
                    continue
                lastIndex = i
                break

            for image in request.files.getlist("images[]"):
                if allowed_file(image.filename):
                    imageFilename = '{:04d}'.format(lastIndex)
                    imagePath = '{}.{}'.format(os.path.join(studentDir, imageFilename),'jpg')
                    image.save(imagePath)
                    lastIndex+=1
        flash('Student editted successfully','success')
        calculateStudentEmbeddings(studentID)
        students = loadStudents()
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
        appDatabase[STUDENTS_COL].delete_many({"ID":id})
        rmtree(os.path.join(STUDENTS_PHOTOS_DIR ,id),ignore_errors=True)
        return redirect('/studentsList')
    return(Response('Invalid delete operation'))

@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)



    
#clean up and free allocated resources

capture.release()


