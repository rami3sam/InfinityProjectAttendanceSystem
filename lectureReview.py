from __main__ import app
import DatabaseClient
from flask import render_template
@app.route('/lectureReview/<int:lectureId>')
def lectureReview(lectureId):


    databaseClient = DatabaseClient.DatabaseClient()
    selectionCriteria = {'lectureId':lectureId}
    lecture = databaseClient.loadDocument(DatabaseClient.LECTURES_COL,DatabaseClient.LECTURE_TAG,selectionCriteria)
    if lecture is None:
        return 'Sorry lecture isnt found'

    lectureLength = lecture['lectureEnd'] - lecture['lectureStart']
    periodPercentage =  ( databaseClient.getTimePeriod() / lectureLength ) * 100
    dates = databaseClient.getDistinctValues(DatabaseClient.ATTENDANCE_COL,DatabaseClient.ATTENDANCE_TAG,'date',selectionCriteria)
    Threshold = databaseClient.getPeriodThreshold()
    
    attendanceInfo = dict()
    for date in dates:
        if attendanceInfo.get(date,None) is None:
            attendanceInfo[date] = dict()

        selectionCriteria = {'date':date,'lectureId':lectureId}
        attendanceList = databaseClient.loadDocuments(DatabaseClient.ATTENDANCE_COL,DatabaseClient.ATTENDANCE_TAG,selectionCriteria)
        for attendance in attendanceList:
            studentName = attendance['name']
            if attendanceInfo[date].get(studentName,None) is None:
                attendanceInfo[date][studentName] = dict()
                attendanceInfo[date][studentName]['name'] = attendance['name']
                attendanceInfo[date][studentName]['timesOfRecogniton'] = 0
                attendanceInfo[date][studentName]['id'] = attendance['id']
           
                attendanceInfo[date][studentName]['attendancePercentage'] = 0
            attendanceInfo[date][studentName]['timesOfRecogniton'] += attendance['timesOfRecogniton']
            if attendance['timesOfRecogniton'] >= Threshold:
                attendanceInfo[date][studentName]['attendancePercentage'] += periodPercentage
    
    return render_template('lectureReview.html',attendanceInfo=attendanceInfo,enumerate=enumerate)
