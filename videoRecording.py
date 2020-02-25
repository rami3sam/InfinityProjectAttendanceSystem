import cv2
import os
import time
import datetime
import multiprocessing
import DatabaseClient
import pytz



def writeVideo(cameraID):
    databaseClient = DatabaseClient.DatabaseClient()
    attendanceJsonOld = None

    disp = 0
    i=1
    os.makedirs('output',exist_ok=True)
    startTime = time.time()
    
    
    fourcc = cv2.VideoWriter_fourcc(*'DIVX')
    frame = cv2.imread(f'shared/CAM_{cameraID}.jpg')
    if frame is None:
        exit(1)
    height, width = frame.shape[:2]
    postFix = f'{cameraID}_{datetime.datetime.now()}'
    videoWriter = cv2.VideoWriter(f'output/CAM_{postFix}.avi', fourcc, 30.0, (width,height))
    print(f'starting to write camera {cameraID} output to harddisk')
    while True:
        frame = cv2.imread(f'shared/CAM_{cameraID}.jpg')
        videoWriter.write(frame)

        attendanceJson = databaseClient.loadDocument(DatabaseClient.SHARED_COL,'STUDENTS_JSON_LIST')
        if attendanceJson is not None: del attendanceJson['_id'];del attendanceJson['documentType']
        if attendanceJson is not None and (attendanceJson != attendanceJsonOld or attendanceJsonOld is None):
            endTime = time.time()
            timeDif = endTime - startTime
            dt = datetime.datetime.fromtimestamp(disp,tz=pytz.utc)
            startTimeStr = '{},{:03d}'.format(dt.strftime('%H:%M:%S'),int(dt.strftime('%f'))//1000)
            
            
            
            dt = datetime.datetime.fromtimestamp(disp+timeDif,tz=pytz.utc)
            endTimeStr ='{},{:03d}'.format(dt.strftime('%H:%M:%S'),int(dt.strftime('%f'))//1000)
            startTime = endTime

            subText = ''
            disp += timeDif
            if attendanceJson is not None:
                for idKey in attendanceJson:
                    student = attendanceJson[idKey]
                    subText+= f'{idKey}:{student["name"]}'

            attendanceJsonOld = attendanceJson
            
            subtitle = f'{i}\n{startTimeStr} --> {endTimeStr}\n{subText}\n\n'
            i+=1

            with open(f'output/CAM_{postFix}.srt','a+') as f:
                print(subtitle,file=f)

 
def startWritingVideo(cameraNumber):
    process = multiprocessing.Process(target=writeVideo,args=[f'{cameraNumber:02d}'])
    process.start()
