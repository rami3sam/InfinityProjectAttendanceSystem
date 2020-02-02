from __main__ import app
from core_functions import appDatabase,STUDENTS_COL,STUDENTS_PHOTOS_DIR
from shutil import rmtree
import os
from flask import Response,redirect,request

@app.route('/deleteStudent/<studentID>')
def deleteStudent(studentID):
    #we query the database to find a student with the ID if it exists we delete it and the associated folder
    if appDatabase[STUDENTS_COL].count_documents({'ID':studentID}) > 0:
        appDatabase[STUDENTS_COL].delete_many({"ID":studentID})
        rmtree(os.path.join(STUDENTS_PHOTOS_DIR ,studentID),ignore_errors=True)
        return redirect('/studentsList')
    else:
        return(Response('Invalid delete operation'))