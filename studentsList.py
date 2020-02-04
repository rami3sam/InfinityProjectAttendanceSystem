from __main__ import app
from core_functions import appDatabase,STUDENTS_COL
from flask import render_template
@app.route('/studentsList/<pageNo>')
def studentsList(pageNo):
    studentsInPage = 10
    pageNo = int(pageNo)
    students = appDatabase[STUDENTS_COL].find().skip(pageNo*10).limit(10)
    return render_template('studentsList.html',students=students)