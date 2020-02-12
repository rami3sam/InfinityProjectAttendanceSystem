from __main__ import app
import DatabaseClient
from flask import render_template
@app.route('/studentsList/<int:pageNo>')
def studentsList(pageNo):
    databaseClient = DatabaseClient.DatabaseClient()
    students = databaseClient.getStudentsList(pageNo,10)
    return render_template('studentsList.html',students=students)