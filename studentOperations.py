from __main__ import app
from flask import request,render_template,Response,flash,redirect
from DatabaseClient import allowed_file,STUDENTS_PHOTOS_DIR
import datetime
import os
from shutil import rmtree
from AppClasses import Student
import DatabaseClient
@app.route('/editStudent/<studentID>',methods=['GET','POST'])
@app.route('/addStudent',methods=['GET','POST'])
def editStudent(studentID=None):
    databaseClient = DatabaseClient.DatabaseClient()
    invalidEditOperation = Response('Invalid edit operation')
    now = datetime.datetime.now() 
    years = databaseClient.getCollegeYears()
    majors = databaseClient.getMajors()
    if request.method == 'GET':
            if studentID is None:
                operation = 'Add'
            else:
                operation = 'Edit'

            student = databaseClient.getStudentByID(studentID,False)
          
            return render_template('studentOperations.html',now=now,majors=majors,
            years=years,student=student,operation=operation)

    if request.method == 'POST':
        studentName = request.form.get('studentName')
        collegeYear = request.form.get('collegeYear')
        admissionYear = request.form.get('admissionYear')
        studentMajor = request.form.get('studentMajor')

        if databaseClient.checkForStudentExistence(studentID):
            student = databaseClient.getStudentByID(studentID,False)
            lastImageIndex = student.lastImageIndex
        else:
            studentID = request.form.get('studentID')
            lastImageIndex = 0
        
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
        
        if databaseClient.checkForStudentExistence(studentID):
            student = databaseClient.getStudentByID(studentID,False)
            databaseClient.deleteStudentByID(studentID)
            flash('Student was editted successfully','success')
        else:
            student =  Student()
            
            flash('Student was added successfully','success')
        
        student.ID = studentID
        student.name = studentName
        student.major = studentMajor
        student.collegeYear = collegeYear
        student.admissionYear = admissionYear
        student.lastImageIndex = lastImageIndex

        studentDict = student.getStudentAsDict()
        databaseClient.insertStudent(studentDict)

        return redirect('/studentsList/0')

@app.route('/deleteStudent/<studentID>')
def deleteStudent(studentID):
    databaseClient = DatabaseClient.DatabaseClient()
    #we query the database to find a student with the ID if it exists we delete it and the associated folder
    if databaseClient.checkForStudentExistence(studentID):
        databaseClient.deleteStudentByID(studentID)
        rmtree(os.path.join(STUDENTS_PHOTOS_DIR ,studentID),ignore_errors=True)
        return redirect('/studentsList/0')
    else:
        return(Response('Invalid delete operation'))