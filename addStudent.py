from __main__ import app
from flask import request,render_template,redirect,flash
from core_functions import appDatabase,STUDENTS_COL,STUDENTS_PHOTOS_DIR,allowed_file,years,majors
from calculateEmbeddings import calculateStudentEmbeddings
import os 
import datetime
@app.route('/addStudent',methods=['GET','POST'])
def addStudent():
    now = datetime.datetime.now() 
    if request.method == 'GET':
        
        return render_template('addStudent.html',now=now,majors=majors,years=years)
    if request.method == 'POST':

        studentName = request.form.get('studentName')
        studentID = request.form.get('studentID')
        collegeYear = request.form.get('collegeYear')
        admissionYear = request.form.get('admissionYear')
        studentMajor = request.form.get('studentMajor')

        
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

        lastImageIndex = 0
        if images:
            studentDir = os.path.join(STUDENTS_PHOTOS_DIR , studentID)
            os.makedirs(studentDir,exist_ok=True)
            for i,image in enumerate(request.files.getlist("images[]")):
                if  allowed_file(image.filename):
                    imageFilename = '{:04d}'.format(i)
                    imagePath = '{}.{}'.format(os.path.join(studentDir, imageFilename),'jpg')
                    image.save(imagePath)
                    lastImageIndex = i
                else:
                    flash('Allowed file types are jpg, jpeg','error')
                    return redirect(request.url)
        
        studentDict = dict(name=studentName,ID=studentID,
        collegeYear=collegeYear,admissionYear=admissionYear,major=studentMajor,
        embeddingsList=[],processedPhotos=[],lastImageIndex=lastImageIndex)
        appDatabase[STUDENTS_COL].insert_one(studentDict)
        calculateStudentEmbeddings(studentID)
        flash('Student added successfully','success')
        return redirect('/addStudent')
