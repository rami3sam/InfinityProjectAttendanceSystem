import cv2
import PIL
import time
from flask import Flask, render_template, Response,make_response

app = Flask(__name__)

def getFrame():
    capture = cv2.VideoCapture(1)
    ret, frame = capture.read()
    capture.release()
    ret, jpeg = cv2.imencode('.jpg', frame)
    return jpeg.tobytes()

@app.route('/photo.jpg')
def video_viewer():
    response = make_response(getFrame())
    response.headers['Content-Type'] = 'image/jpeg'
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8080 ,  threaded=True)

