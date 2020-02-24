from __main__ import app
from flask import request,render_template,redirect,flash
from DatabaseClient import STUDENTS_PHOTOS_DIR,allowed_file
import os 
import datetime
from AppClasses import Student
import DatabaseClient
import utilities

@app.route('/addLecture',methods=['GET','POST'])
def addLecture():
    databaseClient = DatabaseClient.DatabaseClient()
    if request.method == 'GET':
        years = databaseClient.getCollegeYears()
        majors = databaseClient.getMajors()
        days = databaseClient.getDays()
        return render_template('addLecture.html',majors=majors,years=years,days=days)
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
        lectureId = databaseClient.getNextSequenceNumber('lectureId')
        lectureDict = dict(lectureName=lectureName , lectureTeacher=lectureTeacher ,lectureMajor=lectureMajor,
        lectureYear=lectureYear,lectureDay=lectureDay,lectureTime=lectureTime,lectureLength=lectureLength,
        lectureStart=lectureStart,lectureEnd=lectureEnd,lectureId=lectureId)

        databaseClient.saveDocument(DatabaseClient.LECTURES_COL,DatabaseClient.LECTURE_TAG,lectureDict)
        flash('Lecture was added successfully','success')
        return redirect('/addLecture')
