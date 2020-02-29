import cv2
import os
import time
import datetime
import multiprocessing
import DatabaseClient
import pytz

def writeSubtitleSequence(subtitleFilename,subtitleText,sequenceNumber,startTime,endTime):
    startTimeDT = datetime.datetime.fromtimestamp(startTime,tz=pytz.utc)
    endTimeDT = datetime.datetime.fromtimestamp(endTime,tz=pytz.utc)
    
    startTimeFormatted = '{},{:03d}'.format(startTimeDT.strftime('%H:%M:%S'),int(startTimeDT.strftime('%f'))//1000)
    endTimeFormatted ='{},{:03d}'.format(endTimeDT.strftime('%H:%M:%S'),int(endTimeDT.strftime('%f'))//1000)
    subtitle = f'{sequenceNumber}\n{startTimeFormatted} --> {endTimeFormatted}\n{subtitleText}\n'
    with open(subtitleFilename,'a+') as f:
        print(subtitle,file=f)

def writeVideo(cameraID):
    databaseClient = DatabaseClient.DatabaseClient()
    FPS = DatabaseClient.FPS
    postFix = f'{cameraID}_{datetime.datetime.now()}'
    cameraFrameFilename = f'shared/CAM_{cameraID}.jpg'
    subtitleFilename = f'output/CAM_{postFix}.srt'
    videoFilename = f'output/CAM_{postFix}.avi'
    
    os.makedirs('output',exist_ok=True)

    counter=1
    startTime = 0
    attendanceJsonOld = None
    subtitleText = None
    
    fourcc = cv2.VideoWriter_fourcc(*'DIVX')
    frame = cv2.imread(cameraFrameFilename)
    if frame is None:
        exit(1)
    height, width = frame.shape[:2]

    videoWriter = cv2.VideoWriter(videoFilename, fourcc, FPS, (width,height))
    print(f'starting to write camera {cameraID} output to harddisk')
    try:
        while True:
            attendanceJson = databaseClient.loadDocument(DatabaseClient.SHARED_COL,'STUDENTS_JSON_LIST')
            if attendanceJson is not None:
                 del attendanceJson['_id']
                 del attendanceJson['documentType']
    
            if attendanceJson is not None and (attendanceJson != attendanceJsonOld or attendanceJsonOld is None):
                if subtitleText is not None:
                    writeSubtitleSequence(subtitleFilename,subtitleText,counter,startTime,endTime)
    
                startTime = counter*(1/FPS)             
                subtitleText = ''
                
                if attendanceJson is not None:
                    for studentID in attendanceJson:
                        student = attendanceJson[studentID]
                        cameraIDInt = int(cameraID)
                        if cameraIDInt in student['cameraIDs']:
                            cameraIDIndex = student['cameraIDs'].index(cameraIDInt)
                            errorValue = student['errorValues'][cameraIDIndex]
                            subtitleText+= f'{studentID}:{student["studentName"]}:{errorValue:.6f}\n'
    
                attendanceJsonOld = attendanceJson
                if subtitleText == '':
                    subtitleText='No person was detected'

            counter+=1
            endTime = counter*(1/FPS) 
            
            
            frame = cv2.imread(cameraFrameFilename)
            
            videoWriter.write(frame)
            time.sleep(1/FPS)
    except:
        writeSubtitleSequence(subtitleFilename,subtitleText,counter,startTime,endTime)
        
        
def startWritingVideo(cameraNumber):
    process = multiprocessing.Process(target=writeVideo,args=[f'{cameraNumber:02d}'])
    process.start()
    