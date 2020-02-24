from __main__ import app
from flask import request,render_template,Response,flash,redirect
from DatabaseClient import allowed_file,STUDENTS_PHOTOS_DIR
import datetime
import os
from AppClasses import Student
import DatabaseClient
import utilities
@app.route('/editLecture/<int:lectureId>',methods=['GET','POST'])
def editLecture(lectureId):
    databaseClient = DatabaseClient.DatabaseClient()
    invalidEditOperation = Response('Invalid edit operation')
    if request.method == 'GET':
        selectionCriteria = {'lectureId':lectureId}
        years = databaseClient.getCollegeYears()
        majors = databaseClient.getMajors()
        days = databaseClient.getDays()
        lecture = databaseClient.loadDocument(DatabaseClient.LECTURES_COL,DatabaseClient.LECTURE_TAG,selectionCriteria)
        if lecture is None:
            return invalidEditOperation
        return render_template('editLecture.html',majors=majors,years=years,days=days,lecture=lecture)
    if request.method == 'POST':
        lectureName = request.form.get('lectureName')
        lectureTeacher = request.form.get('lectureTeacher')
        lectureMajor = request.form.get('lectureMajor')
        lectureYear = request.form.get('lectureYear')
        lectureDay = request.form.get('lectureDay')
        lectureTime = request.form.get('lectureTime')
        lectureLength = request.form.get('lectureLength')

        lectureStart = utilities.changeTimeFormat(lectureTime)
        lectureEnd=lectureStart+(int(lectureLength)*3600)

        lectureDict = dict(lectureName=lectureName , lectureTeacher=lectureTeacher ,lectureMajor=lectureMajor,
        lectureYear=lectureYear,lectureDay=lectureDay,lectureTime=lectureTime,lectureLength=lectureLength,
        lectureStart=lectureStart,lectureEnd=lectureEnd,lectureId=lectureId)

        selectionCriteria = {'lectureId':lectureId}
        lectureDocument = databaseClient.loadDocument(DatabaseClient.LECTURES_COL,DatabaseClient.LECTURE_TAG,selectionCriteria)
        if lectureDocument:
            databaseClient.deleteDocument(DatabaseClient.LECTURES_COL,DatabaseClient.LECTURE_TAG,selectionCriteria)
            databaseClient.saveDocument(DatabaseClient.LECTURES_COL,DatabaseClient.LECTURE_TAG,lectureDict)
            flash('Lecture was added successfully','success')
        else:
            return invalidEditOperation
        return redirect(f'/editLecture/{lectureId}')
