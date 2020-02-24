from __main__ import app
from flask import request,render_template,Response,flash,redirect
from DatabaseClient import allowed_file,STUDENTS_PHOTOS_DIR
import datetime
import os
from AppClasses import Student
import DatabaseClient
import utilities
@app.route('/editLecture/<int:lectureId>',methods=['GET','POST'])
@app.route('/addLecture',methods=['GET','POST'])
def editLecture(lectureId=None):
    databaseClient = DatabaseClient.DatabaseClient()
    invalidEditOperation = Response('Invalid edit operation')
    if request.method == 'GET':
        selectionCriteria = {'lectureId':lectureId}
        years = databaseClient.getCollegeYears()
        majors = databaseClient.getMajors()
        days = databaseClient.getDays()
        lecture = databaseClient.loadDocument(DatabaseClient.LECTURES_COL,DatabaseClient.LECTURE_TAG,selectionCriteria)
        if lecture is None:
            if lectureId is not None:
                return invalidEditOperation

        if lectureId is None:
            operation = 'Add'
        else:
            operation = 'Edit'

        return render_template('lectureOperations.html',majors=majors,years=years,days=days,lecture=lecture,operation=operation)
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

        

        selectionCriteria = {'lectureId':lectureId}
        
        if lectureId is not None:
            if databaseClient.loadDocument(DatabaseClient.LECTURES_COL,DatabaseClient.LECTURE_TAG,selectionCriteria):
                databaseClient.deleteDocument(DatabaseClient.LECTURES_COL,DatabaseClient.LECTURE_TAG,selectionCriteria)
                flash('Lecture was edited successfully','success')
            else:
                return invalidEditOperation
            
        else:
            lectureId = databaseClient.getNextSequenceNumber('lectureId')
            flash('Lecture was added successfully','success')
            
        lectureDict = dict(lectureName=lectureName , lectureTeacher=lectureTeacher ,lectureMajor=lectureMajor,
        lectureYear=lectureYear,lectureDay=lectureDay,lectureTime=lectureTime,lectureLength=lectureLength,
        lectureStart=lectureStart,lectureEnd=lectureEnd,lectureId=lectureId)

        databaseClient.saveDocument(DatabaseClient.LECTURES_COL,DatabaseClient.LECTURE_TAG,lectureDict)
        return redirect('/lecturesList/0')

@app.route('/deleteLecture/<int:lectureId>')
def deleteLecture(lectureId):
     
    databaseClient = DatabaseClient.DatabaseClient()
    #we query the database to find a student with the ID if it exists we delete it and the associated folder
    selectionCriteria = {'lectureId' : lectureId}
    if databaseClient.loadDocument(DatabaseClient.LECTURES_COL,DatabaseClient.LECTURE_TAG,selectionCriteria):
        databaseClient.deleteDocument(DatabaseClient.LECTURES_COL,DatabaseClient.LECTURE_TAG,selectionCriteria)
        return redirect('/lecturesList/0')
    else:
        return(Response('Invalid delete operation'))