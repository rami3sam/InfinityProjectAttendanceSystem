import cv2
import os
import time
import datetime
import multiprocessing
import DatabaseClient
databaseClient = DatabaseClient.DatabaseClient()
def writeVideo(cameraID):
    os.makedirs('output',exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*'DIVX')
    frame = cv2.imread(f'shared/CAM_{cameraID}.jpg')
    height, width = frame.shape[:2]
    videoWriter = cv2.VideoWriter(f'output/CAM_{cameraID}_{datetime.datetime.now()}.avi', fourcc, 30.0, (width,height))
    print(f'starting to write camera {cameraID} output to harddisk')
    while True:
        frame = cv2.imread(f'shared/CAM_{cameraID}.jpg')
        videoWriter.write(frame)
        time.sleep(1/30)

def startWritingVideo():
    CAMERA_IP_ADDRESSES  = databaseClient.getSettings('cameraIPS',['127.0.0.1:5000'])
    CAM_NO = len(CAMERA_IP_ADDRESSES)

    for cameraNumber in range(CAM_NO):
        process = multiprocessing.Process(target=writeVideo,args=[f'{cameraNumber:02d}'])
        process.start()
