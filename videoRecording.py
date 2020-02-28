import cv2
import os
import time
import datetime
import multiprocessing
import DatabaseClient
import pytz



def writeVideo(cameraID):
    databaseClient = DatabaseClient.DatabaseClient()
    FPS = DatabaseClient.FPS
    attendanceJsonOld = None
 
    i=1
    os.makedirs('output',exist_ok=True)
    startTime = 0
    subText = None
    
    fourcc = cv2.VideoWriter_fourcc(*'DIVX')
    frame = cv2.imread(f'shared/CAM_{cameraID}.jpg')
    if frame is None:
        exit(1)
    height, width = frame.shape[:2]
    postFix = f'{cameraID}_{datetime.datetime.now()}'

    videoWriter = cv2.VideoWriter(f'output/CAM_{postFix}.avi', fourcc, FPS, (width,height))
    print(f'starting to write camera {cameraID} output to harddisk')
    while True:
        attendanceJson = databaseClient.loadDocument(DatabaseClient.SHARED_COL,'STUDENTS_JSON_LIST')
        if attendanceJson is not None: del attendanceJson['_id'];del attendanceJson['documentType']

        if attendanceJson is not None and (attendanceJson != attendanceJsonOld or attendanceJsonOld is None):
            if subText is not None:
                subtitle = f'{i}\n{startTimeStr} --> {endTimeStr}\n{subText}\n'
                with open(f'output/CAM_{postFix}.srt','a+') as f:
                    print(subtitle,file=f)

            startTime = i*(1/FPS) 
            dt = datetime.datetime.fromtimestamp(startTime,tz=pytz.utc)
            startTimeStr = '{},{:03d}'.format(dt.strftime('%H:%M:%S'),int(dt.strftime('%f'))//1000)
        
            subText = ''
            
            if attendanceJson is not None:
                for idKey in attendanceJson:
                    student = attendanceJson[idKey]
                    subText+= f'{idKey}:{student["name"]}'

            attendanceJsonOld = attendanceJson
            if subText == '':
                subText='No person was detected'

        endTime = i*(1/FPS) 
        dt = datetime.datetime.fromtimestamp(endTime,tz=pytz.utc)
        endTimeStr ='{},{:03d}'.format(dt.strftime('%H:%M:%S'),int(dt.strftime('%f'))//1000)
   

            
        i+=1
        frame = cv2.imread(f'shared/CAM_{cameraID}.jpg')
        videoWriter.write(frame)
        time.sleep(1/FPS)
def startWritingVideo(cameraNumber):
    process = multiprocessing.Process(target=writeVideo,args=[f'{cameraNumber:02d}'])
    process.start()
