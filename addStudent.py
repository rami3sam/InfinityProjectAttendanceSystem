from __main__ import app
from flask import request,render_template,redirect,flash
from DatabaseClient import STUDENTS_PHOTOS_DIR,allowed_file
import os 
import datetime
from AppClasses import Student
import DatabaseClient
@app.route('/addStudent',methods=['GET','POST'])
def addStudent():
    databaseClient = DatabaseClient.DatabaseClient()
    now = datetime.datetime.now() 
    if request.method == 'GET':
        years = databaseClient.getCollegeYears()
        majors = databaseClient.getMajors()
        return render_template('addStudent.html',now=now,majors=majors,years=years)
    if request.method == 'POST':

        studentName = request.form.get('studentName')
        studentID = request.form.get('studentID')
        collegeYear = request.form.get('collegeYear')
        admissionYear = request.form.get('admissionYear')
        studentMajor = request.form.get('studentMajor')

        
        if databaseClient.checkForStudentExistence(studentID):
            flash('Student ID must be unique','danger')
            return redirect(request.url)


        if 'images[]' not in request.files:
            flash('You must select at least one image','danger')
            return redirect(request.url)
		
        images = request.files['images[]']
        if images.filename == '':
            flash('You must select at least one image','danger')
            return redirect(request.url)
        
        studentDir = os.path.join(STUDENTS_PHOTOS_DIR , studentID)
        os.makedirs(studentDir,exist_ok=True)
        for i,image in enumerate(request.files.getlist("images[]")):
            if  allowed_file(image.filename):
                imageFilename = '{:04d}'.format(i)
                imagePath = '{}.{}'.format(os.path.join(studentDir, imageFilename),'jpg')
                image.save(imagePath)
                lastImageIndex = i
            else:
                flash('Allowed file types are jpg, jpeg','danger')
                return redirect(request.url)
                
        student = Student()
        student.ID = studentID
        student.name = studentName
        student.major = studentMajor
        student.collegeYear = collegeYear
        student.admissionYear = admissionYear
        student.lastImageIndex = lastImageIndex

        studentDict = student.getStudentAsDict()
        databaseClient.insertStudent(studentDict)
      
        flash('Student was added successfully','success')
        return redirect('/addStudent')
