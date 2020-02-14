from __main__ import app
from DatabaseClient import STUDENTS_PHOTOS_DIR
from shutil import rmtree
import os
from flask import Response,redirect,request
import DatabaseClient
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