from __main__ import app
from flask import request,render_template,Response,flash,redirect
from calculateEmbeddings import calculateStudentEmbeddings
from core_functions import appDatabase,STUDENTS_COL,years,majors,\
allowed_file,STUDENTS_PHOTOS_DIR,checkForStudentExistence,getStudentByID
import datetime
import os
from classes import Student
@app.route('/editStudent/<studentID>',methods=['GET','POST'])
def editStudent(studentID):
    invalidEditOperation = Response('Invalid edit operation')
    now = datetime.datetime.now() 
    if request.method == 'GET':
            if checkForStudentExistence(studentID):
                student = getStudentByID(studentID,False)
                return render_template('editStudent.html',now=now,majors=majors,
                years=years,student=student)
            else:
                return invalidEditOperation
   
    if request.method == 'POST':
        studentName = request.form.get('studentName')
        collegeYear = request.form.get('collegeYear')
        admissionYear = request.form.get('admissionYear')
        studentMajor = request.form.get('studentMajor')

        if checkForStudentExistence(studentID):
            student = getStudentByID(studentID,False)
            lastImageIndex = student.lastImageIndex
        else:
            return invalidEditOperation
        
        images = request.files['images[]']
        if images and not images.filename == '':
            studentDir = os.path.join(STUDENTS_PHOTOS_DIR , studentID)          
            os.makedirs(studentDir,exist_ok=True)
            for image in request.files.getlist("images[]"):
                if allowed_file(image.filename):
                    lastImageIndex+=1
                    imageFilename = '{:04d}'.format(lastImageIndex)
                    imagePath = '{}.{}'.format(os.path.join(studentDir, imageFilename),'jpg')
                    image.save(imagePath)
                else:
                    flash('Allowed file types are jpg, jpeg','danger')
                    return redirect(request.url)
        

        student = student = getStudentByID(studentID,False)
        studentDict = student.getStudentAsDict()
        
        if checkForStudentExistence(studentID):
            appDatabase[STUDENTS_COL].delete_many({'ID':studentID})
            appDatabase[STUDENTS_COL].insert_one(studentDict)

        calculateStudentEmbeddings(studentID)
        flash('Student editted successfully','success')
        return redirect(request.url)