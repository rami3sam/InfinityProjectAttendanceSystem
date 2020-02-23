from __main__ import app
import DatabaseClient
from flask import render_template
@app.route('/lecturesList/<int:pageNo>')
def lecturesList(pageNo):
    databaseClient = DatabaseClient.DatabaseClient()
    lectures = databaseClient.loadDocuments(DatabaseClient.LECTURES_COL,DatabaseClient.LECTURE_TAG)
    return render_template('lecturesList.html',lectures=lectures)
