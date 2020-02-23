from __main__ import app
from flask import request,render_template,Response,flash,redirect
from DatabaseClient import allowed_file,STUDENTS_PHOTOS_DIR
import datetime
import os
from AppClasses import Student
import DatabaseClient
@app.route('/editLecture/<lectureName>',methods=['GET','POST'])
def editLecture(lectureName):
    databaseClient = DatabaseClient.DatabaseClient()
    invalidEditOperation = Response('Invalid edit operation')
    if request.method == 'GET':
        selectionCriteria = {'lectureName':lectureName}
        years = databaseClient.getCollegeYears()
        majors = databaseClient.getMajors()
        days = databaseClient.getDays()
        lecture = databaseClient.loadDocument(DatabaseClient.LECTURES_COL,DatabaseClient.LECTURE_TAG,selectionCriteria)
        if lecture is None:
            return invalidEditOperation
        return render_template('editLecture.html',majors=majors,years=years,days=days,lecture=lecture)
    if request.method == 'POST':

        oldLectureName = request.form.get('oldLectureName')
        lectureName = request.form.get('lectureName')
        lectureTeacher = request.form.get('lectureTeacher')
        lectureMajor = request.form.get('lectureMajor')
        lectureYear = request.form.get('lectureYear')
        lectureDay = request.form.get('lectureDay')
        lectureTime = request.form.get('lectureTime')
        lectureLength = request.form.get('lectureLength')

        lectureDict = dict(lectureName=lectureName , lectureTeacher=lectureTeacher ,lectureMajor=lectureMajor,
        lectureYear=lectureYear,lectureDay=lectureDay,lectureTime=lectureTime,lectureLength=lectureLength)
        selectionCriteria = {'lectureName':oldLectureName}
        if databaseClient.loadDocument(DatabaseClient.LECTURES_COL,DatabaseClient.LECTURE_TAG,selectionCriteria):
            databaseClient.deleteDocument(DatabaseClient.LECTURES_COL,DatabaseClient.LECTURE_TAG,selectionCriteria)
            databaseClient.saveDocument(DatabaseClient.LECTURES_COL,DatabaseClient.LECTURE_TAG,lectureDict)
            flash('Lecture was added successfully','success')
        else:
            return invalidEditOperation
        return redirect(f'/editLecture/{lectureName}')
