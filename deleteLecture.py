from __main__ import app
from DatabaseClient import STUDENTS_PHOTOS_DIR
from shutil import rmtree
import os
from flask import Response,redirect,request
import DatabaseClient
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