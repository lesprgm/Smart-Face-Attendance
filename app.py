from flask import Flask, render_template, Response, request, redirect, url_for, jsonify, send_from_directory, session
import cv2
import os
from datetime import datetime
import json
import face_recognition
import numpy as np

app = Flask(__name__)
app.secret_key = os.urandom(24)


known_face_encodings = []
known_face_names = []

def load_known_faces():
    global known_face_encodings, known_face_names
    known_face_encodings = []
    known_face_names = []
    
    faces_dir = 'faces'
    if not os.path.exists(faces_dir):
        os.makedirs(faces_dir)
    
    for filename in os.listdir(faces_dir):
        if filename.endswith('.jpg'):
            name = filename[:-4]
            image_path = os.path.join(faces_dir, filename)
            print(f"Loading face: {image_path}")
            
            image = face_recognition.load_image_file(image_path)
            face_encodings = face_recognition.face_encodings(image)
            
            if face_encodings:
                known_face_encodings.append(face_encodings[0])
                known_face_names.append(name)
                print(f"Successfully loaded face: {name}")
            else:
                print(f"No face detected in: {filename}")

load_known_faces()

video_capture = None
last_attendance_check = {}

def get_video_capture():
    global video_capture
    if video_capture is None:
        video_capture = cv2.VideoCapture(0)
        video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    return video_capture

def generate_frames():
    frame_count = 0
    while True:
        video_capture = get_video_capture()
        ret, frame = video_capture.read()
        if not ret:
            break
            
        frame_count += 1
        if frame_count % 2 != 0:
            continue
            
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            top *= 2
            right *= 2
            bottom *= 2
            left *= 2
            
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"
            
            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]
                
                current_time = datetime.now()
                if name not in last_attendance_check or \
                   (current_time - last_attendance_check[name]).total_seconds() > 300:
                    record_attendance(name)
                    last_attendance_check[name] = current_time
                    print(f"Recording attendance for {name}")
            
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)
        
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def record_attendance(name):
    try:
        attendance_dir = 'static/attendance'
        if not os.path.exists(attendance_dir):
            os.makedirs(attendance_dir)
        
        current_date = datetime.now().strftime('%Y-%m-%d')
        current_time = datetime.now().strftime('%H:%M:%S')
        attendance_file = os.path.join(attendance_dir, f'{current_date}.json')
        
        attendance_data = []
        if os.path.exists(attendance_file):
            with open(attendance_file, 'r') as f:
                attendance_data = json.load(f)
        
        for entry in attendance_data:
            if entry['name'] == name and entry['date'] == current_date:
                print(f"Attendance already recorded for {name} today")
                return
        
        new_record = {
            'name': name,
            'date': current_date,
            'time': current_time
        }
        attendance_data.append(new_record)
        
        with open(attendance_file, 'w') as f:
            json.dump(attendance_data, f, indent=4)
        
        print(f"Attendance recorded for {name} at {current_time}")
    except Exception as e:
        print(f"Error recording attendance: {str(e)}")

@app.route('/')
def index():
    if not session.get('privacy_notice_accepted'):
        return redirect(url_for('privacy_notice'))
    return render_template('index.html')

@app.route('/privacy_notice', methods=['GET', 'POST'])
def privacy_notice():
    if request.method == 'POST':
        session['privacy_notice_accepted'] = True
        return redirect(url_for('index'))
    return render_template('privacy_notice.html')

@app.route('/set_privacy_notice', methods=['POST'])
def set_privacy_notice():
    session['privacy_notice_accepted'] = True
    return jsonify({'success': True})

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        image = request.files['image']
        
        if name and image:
            faces_dir = 'faces'
            if not os.path.exists(faces_dir):
                os.makedirs(faces_dir)
            
            image_path = os.path.join(faces_dir, f'{name}.jpg')
            image.save(image_path)
            print(f"Saved image to: {image_path}")
            
            image = face_recognition.load_image_file(image_path)
            face_encodings = face_recognition.face_encodings(image)
            
            if face_encodings:
                load_known_faces()
                return render_template('register.html', success=True, name=name)
            else:
                os.remove(image_path)
                return render_template('register.html', error="No face detected in the image")
    
    return render_template('register.html')

@app.route('/view_faces')
def view_faces():
    faces = []
    faces_dir = 'faces'
    if os.path.exists(faces_dir):
        for filename in os.listdir(faces_dir):
            if filename.endswith('.jpg'):
                name = filename[:-4]
                faces.append({
                    'name': name,
                    'image_path': url_for('serve_face', filename=filename)
                })
    return render_template('view_faces.html', faces=faces)

@app.route('/attendance')
def attendance():
    attendance_data = []
    attendance_dir = 'static/attendance'
    if os.path.exists(attendance_dir):
        for filename in os.listdir(attendance_dir):
            if filename.endswith('.json'):
                date = filename[:-5]
                with open(os.path.join(attendance_dir, filename), 'r') as f:
                    data = json.load(f)
                    attendance_data.extend(data)
    
    attendance_data.sort(key=lambda x: (x['date'], x['time']), reverse=True)
    return render_template('attendance.html', attendance=attendance_data)

@app.route('/faces/<filename>')
def serve_face(filename):
    return send_from_directory('faces', filename)

if __name__ == "__main__":
    import os
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
