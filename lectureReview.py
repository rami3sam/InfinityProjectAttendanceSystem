from __main__ import app
import DatabaseClient
from flask import render_template
@app.route('/lectureReview/<int:lectureId>')
def lectureReview(lectureId):
    databaseClient = DatabaseClient.DatabaseClient()
    selectionCriteria = {'lectureId':lectureId}
    dates = databaseClient.getDistinctValues(DatabaseClient.ATTENDANCE_COL,DatabaseClient.ATTENDANCE_TAG,'date',selectionCriteria)
    print([attendance for attendance in dates])
    attendanceInfo = dict()
    for date in dates:
        if attendanceInfo.get(date,None) is None:
            attendanceInfo[date] = dict()

        selectionCriteria = {'date':date}
        attendanceList = databaseClient.loadDocuments(DatabaseClient.ATTENDANCE_COL,DatabaseClient.ATTENDANCE_TAG,selectionCriteria)
        for attendance in attendanceList:
            studentName = attendance['name']
            if attendanceInfo[date].get(studentName,None) is None:
                attendanceInfo[date][studentName] = dict()
                attendanceInfo[date][studentName]['name'] = attendance['name']
                attendanceInfo[date][studentName]['timesOfRecogniton'] = 0
            
            attendanceInfo[date][studentName]['timesOfRecogniton'] += attendance['timesOfRecogniton']
    
    return render_template('lectureReview.html',attendanceInfo=attendanceInfo,enumerate=enumerate)
