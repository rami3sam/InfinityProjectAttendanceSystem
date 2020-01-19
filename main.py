import cv2
capture = cv2.VideoCapture(0)
while(True):
     
    ret, frame = capture.read()
    cv2.imshow('video', frame)
     
    if cv2.waitKey(1) == 27:
        break
capture.release()
cv2.destroyAllWindows()
