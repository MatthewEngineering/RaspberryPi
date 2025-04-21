# Dont forget: wget https://github.com/opencv/opencv/raw/master/data/haarcascades/haarcascade_frontalface_default.xml

from flask import Flask, render_template_string, Response, redirect, url_for, send_file
from picamera2 import Picamera2
import cv2
import threading
import time
import os

app = Flask(__name__)
camera = Picamera2()
camera.configure(camera.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
camera.start()

streaming = False
image_original_path = "static/latest.jpg"
image_processed_path = "static/latest_processed.jpg"

# Load Haar cascade
face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

# HTML Template
HTML = """
<!doctype html>
<html>
<head>
    <title>Pi Camera</title>
</head>
<body>
    <h1>Hello Beesee</h1>
    <form action="{{ url_for('toggle_stream') }}" method="post">
        <button type="submit">{{ 'Stop' if streaming else 'Start' }} Stream</button>
    </form>

    {% if streaming %}
        <img src="{{ url_for('video_feed') }}" width="640" height="480">
    {% endif %}

    <form action="{{ url_for('take_picture') }}" method="post">
        <button type="submit">Take Picture</button>
    </form>

    {% if show_images %}
    <h2>Captured Images:</h2>
    <div style="display: flex; gap: 20px;">
        <div>
            <p>Original</p>
            <img src="{{ url_for('static', filename='latest.jpg') }}" width="320">
        </div>
        <div>
            <p>With Faces</p>
            <img src="{{ url_for('static', filename='latest_processed.jpg') }}" width="320">
        </div>
    </div>
    {% endif %}
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML, streaming=streaming, show_images=os.path.exists(image_original_path))

@app.route('/toggle_stream', methods=['POST'])
def toggle_stream():
    global streaming
    streaming = not streaming
    return redirect(url_for('index'))

def generate_frames():
    while streaming:
        frame = camera.capture_array()
        ret, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        time.sleep(0.05)

@app.route('/video_feed')
def video_feed():
    if not streaming:
        return "Streaming is off", 503
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/take_picture', methods=['POST'])
def take_picture():
    frame = camera.capture_array()
    cv2.imwrite(image_original_path, frame)

    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    cv2.imwrite(image_processed_path, frame)

    return redirect(url_for('index'))

if __name__ == '__main__':
    os.makedirs("static", exist_ok=True)
    app.run(host='0.0.0.0', port=5000)
