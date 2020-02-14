from __main__ import app
from flask import request,render_template,Response,flash,redirect
from DatabaseClient import allowed_file,STUDENTS_PHOTOS_DIR
import datetime
import os
from AppClasses import Student
import DatabaseClient
@app.route('/editStudent/<studentID>',methods=['GET','POST'])
def editStudent(studentID):
    databaseClient = DatabaseClient.DatabaseClient()
    invalidEditOperation = Response('Invalid edit operation')
    now = datetime.datetime.now() 
    years = databaseClient.getCollegeYears()
    majors = databaseClient.getMajors()
    if request.method == 'GET':
            if databaseClient.checkForStudentExistence(studentID):
                student = databaseClient.getStudentByID(studentID,False)
                return render_template('editStudent.html',now=now,majors=majors,
                years=years,student=student)
            else:
                return invalidEditOperation
   
    if request.method == 'POST':
        studentName = request.form.get('studentName')
        collegeYear = request.form.get('collegeYear')
        admissionYear = request.form.get('admissionYear')
        studentMajor = request.form.get('studentMajor')

        if databaseClient.checkForStudentExistence(studentID):
            student = databaseClient.getStudentByID(studentID,False)
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
        

        student = databaseClient.getStudentByID(studentID,False)
        student.name = studentName
        student.admissionYear = admissionYear
        student.collegeYear = collegeYear
        student.major = studentMajor
        studentDict = student.getStudentAsDict()
        
        if databaseClient.checkForStudentExistence(studentID):
            databaseClient.deleteStudentByID(studentID)
            databaseClient.insertStudent(studentDict)

        flash('Student editted successfully','success')
        return redirect(request.url)