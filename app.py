import qrcode
from flask import Flask, render_template, Response, request, redirect, url_for, send_file
import cv2
import face_recognition
import numpy as np
import os
import sqlite3
import math

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize attendance database
def init_db():
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    name TEXT, 
                    confidence TEXT, 
                    time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

# Function to calculate confidence level
def face_confidence(face_distance, face_match_threshold=0.6):
    range_val = (1.0 - face_match_threshold)
    linear_val = (1.0 - face_distance) / (range_val * 2.0)

    if face_distance > face_match_threshold:
        return str(round(linear_val * 100, 2)) + '%'
    else:
        value = (linear_val + ((1.0 - linear_val) * math.pow((linear_val - 0.5) * 2, 0.2))) * 100
        return str(round(value, 2)) + '%'

# Load known faces
known_face_encodings = []
known_face_names = []

def encode_faces():
    known_face_encodings.clear()
    known_face_names.clear()

    for image in os.listdir(UPLOAD_FOLDER):
        face_image = face_recognition.load_image_file(f'{UPLOAD_FOLDER}{image}')
        face_encoding = face_recognition.face_encodings(face_image)
        if face_encoding:
            known_face_encodings.append(face_encoding[0])
            known_face_names.append(os.path.splitext(image)[0])

encode_faces()

# Capture video from webcam
video_capture = cv2.VideoCapture(0)

def log_attendance(name, confidence):
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute("INSERT INTO attendance (name, confidence) VALUES (?, ?)", (name, confidence))
    conn.commit()
    conn.close()

def generate_frames():
    while True:
        success, frame = video_capture.read()
        if not success:
            break
        else:
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_names = []
            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"
                confidence = "Unknown"

                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)

                if matches[best_match_index]:
                    name = known_face_names[best_match_index]
                    confidence = face_confidence(face_distances[best_match_index])
                    log_attendance(name, confidence)

                face_names.append(f"{name} ({confidence})")

            # Draw rectangles and labels
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), -1)
                cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/camera_issue')
def camera_issue():
    return render_template('camera_issue.html')

@app.route('/qr_code')
def qr_code():
    return send_file("static/qr_code.png", mimetype="image/png")

# Generate a QR code for troubleshooting
def generate_qr_code():
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data("https://support.google.com/chrome/answer/2693767?hl=en")  # Replace with actual troubleshooting link
    qr.make(fit=True)

    img = qr.make_image(fill="black", back_color="white")
    qr_path = "static/qr_code.png"
    img.save(qr_path)

generate_qr_code()  # Generate QR code on startup

if __name__ == "__main__":
    app.run(debug=True)
