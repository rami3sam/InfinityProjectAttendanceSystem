from __main__ import app
from core_functions import appDatabase,STUDENTS_COL
from flask import render_template
@app.route('/studentsList')
def studentsList():
    students = appDatabase[STUDENTS_COL].find().skip(0).limit(10)
    return render_template('studentsList.html',students=students)