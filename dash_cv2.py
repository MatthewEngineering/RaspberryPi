# This is an untested version of the cv2 with dash

import dash
from dash import html, dcc, Output, Input, State
import dash_bootstrap_components as dbc
import base64
import cv2
import numpy as np
from picamera2 import Picamera2
import os

# Initialize camera
camera = Picamera2()
camera.configure(camera.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
camera.start()

# Load Haar cascade
face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

# Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Face Detection App"

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Hello Beesee 👋", className="text-center text-primary mb-4"))
    ]),dfasf

    dbc.Row([
        dbc.Col(dbc.Button("Take Picture", id="take-pic-btn", color="primary", className="mb-3"), width="auto")
    ]),

    dbc.Row([
        dbc.Col([html.H5("Original Image"), html.Img(id="original-img", style={"width": "100%"})], width=6),
        dbc.Col([html.H5("Processed Image"), html.Img(id="processed-img", style={"width": "100%"})], width=6)
    ])
], fluid=True)


def capture_and_process():
    frame = camera.capture_array()

    # Save original
    _, original_buffer = cv2.imencode('.jpg', frame)
    original_b64 = base64.b64encode(original_buffer).decode('utf-8')

    # Detect faces
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Encode processed
    _, processed_buffer = cv2.imencode('.jpg', frame)
    processed_b64 = base64.b64encode(processed_buffer).decode('utf-8')

    return original_b64, processed_b64


@app.callback(
    Output("original-img", "src"),
    Output("processed-img", "src"),
    Input("take-pic-btn", "n_clicks"),
    prevent_initial_call=True
)
def update_images(n):
    original_b64, processed_b64 = capture_and_process()
    return f"data:image/jpeg;base64,{original_b64}", f"data:image/jpeg;base64,{processed_b64}"


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
