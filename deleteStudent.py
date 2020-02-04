from __main__ import app
from core_functions import appDatabase,STUDENTS_COL,STUDENTS_PHOTOS_DIR,checkForStudentExistence
from shutil import rmtree
import os
from flask import Response,redirect,request

@app.route('/deleteStudent/<studentID>')
def deleteStudent(studentID):
    #we query the database to find a student with the ID if it exists we delete it and the associated folder
    if checkForStudentExistence(studentID):
        appDatabase[STUDENTS_COL].delete_many({"ID":studentID})
        rmtree(os.path.join(STUDENTS_PHOTOS_DIR ,studentID),ignore_errors=True)
        return redirect('/studentsList/0')
    else:
        return(Response('Invalid delete operation'))