from flask import Flask, render_template, Response, request, redirect, url_for, jsonify, send_from_directory, session
import cv2
import os
from datetime import datetime
import json
import face_recognition
import numpy as np

# Constants
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
FRAME_RESIZE_FACTOR = 0.5
FRAME_SCALE_FACTOR = 2
ATTENDANCE_CHECK_INTERVAL = 300  # seconds (5 minutes)
FACES_DIRECTORY = 'faces'
ATTENDANCE_DIRECTORY = 'static/attendance'
SUPPORTED_IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png')
RECTANGLE_COLOR = (0, 255, 0)  # Green
RECTANGLE_THICKNESS = 2
TEXT_COLOR = (255, 255, 255)  # White
TEXT_SCALE = 0.5

app = Flask(__name__)
app.secret_key = os.urandom(24)


known_face_encodings = []
known_face_names = []

def load_known_faces():
    global known_face_encodings, known_face_names
    known_face_encodings = []
    known_face_names = []
    
    if not os.path.exists(FACES_DIRECTORY):
        os.makedirs(FACES_DIRECTORY)
    
    for filename in os.listdir(FACES_DIRECTORY):
        if filename.endswith(SUPPORTED_IMAGE_EXTENSIONS):
            name = filename[:-4]  # Remove extension
            image_path = os.path.join(FACES_DIRECTORY, filename)
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
        video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
    return video_capture

def generate_frames():
    global video_capture
    frame_count = 0
    while True:
        # Check if video_capture is None (manually stopped) before trying to get it
        if video_capture is None:
            break
            
        if not video_capture.isOpened():
            break
            
        ret, frame = video_capture.read()
        if not ret:
            break
            
        frame_count += 1
        if frame_count % 2 != 0:
            continue
            
        small_frame = cv2.resize(frame, (0, 0), fx=FRAME_RESIZE_FACTOR, fy=FRAME_RESIZE_FACTOR)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            top *= FRAME_SCALE_FACTOR
            right *= FRAME_SCALE_FACTOR
            bottom *= FRAME_SCALE_FACTOR
            left *= FRAME_SCALE_FACTOR
            
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"
            
            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]
                
                current_time = datetime.now()
                if name not in last_attendance_check or \
                   (current_time - last_attendance_check[name]).total_seconds() > ATTENDANCE_CHECK_INTERVAL:
                    record_attendance(name)
                    last_attendance_check[name] = current_time
                    print(f"Recording attendance for {name}")
            
            cv2.rectangle(frame, (left, top), (right, bottom), RECTANGLE_COLOR, RECTANGLE_THICKNESS)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), RECTANGLE_COLOR, cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, TEXT_SCALE, TEXT_COLOR, 1)
        
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def record_attendance(name):
    try:
        if not os.path.exists(ATTENDANCE_DIRECTORY):
            os.makedirs(ATTENDANCE_DIRECTORY)
        
        current_date = datetime.now().strftime('%Y-%m-%d')
        current_time = datetime.now().strftime('%H:%M:%S')
        attendance_file = os.path.join(ATTENDANCE_DIRECTORY, f'{current_date}.json')
        
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
    # Initialize video capture when feed is requested
    get_video_capture()
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/stop_video_feed', methods=['POST'])
def stop_video_feed():
    """Stop the video feed and release camera resources"""
    global video_capture
    try:
        if video_capture is not None:
            video_capture.release()
            video_capture = None
            print("Video capture released successfully")
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error stopping video feed: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        image = request.files['image']
        
        if name and image:
            if not os.path.exists(FACES_DIRECTORY):
                os.makedirs(FACES_DIRECTORY)
            
            image_path = os.path.join(FACES_DIRECTORY, f'{name}.jpg')
            image.save(image_path)
            print(f"Saved image to: {image_path}")
            
            image = face_recognition.load_image_file(image_path)
            face_encodings = face_recognition.face_encodings(image)
            
            if face_encodings:
                load_known_faces()
                # Check if request expects JSON response
                if request.headers.get('Content-Type') == 'application/json' or request.is_json:
                    return jsonify({'success': True, 'name': name})
                return render_template('register.html', success=True, name=name)
            else:
                os.remove(image_path)
                # Check if request expects JSON response
                if request.headers.get('Content-Type') == 'application/json' or request.is_json:
                    return jsonify({'success': False, 'error': "No face detected in the image"})
                return render_template('register.html', error="No face detected in the image")
        else:
            # Check if request expects JSON response
            if request.headers.get('Content-Type') == 'application/json' or request.is_json:
                return jsonify({'success': False, 'error': "Name and image are required"})
            return render_template('register.html', error="Name and image are required")
    
    return render_template('register.html')

@app.route('/view_faces')
def view_faces():
    faces = []
    if os.path.exists(FACES_DIRECTORY):
        for filename in os.listdir(FACES_DIRECTORY):
            if filename.endswith(SUPPORTED_IMAGE_EXTENSIONS):
                name = os.path.splitext(filename)[0]  # Remove extension properly
                faces.append({
                    'name': name,
                    'image_path': url_for('serve_face', filename=filename)
                })
    return render_template('view_faces.html', faces=faces)

@app.route('/attendance')
def attendance():
    attendance_data = []
    if os.path.exists(ATTENDANCE_DIRECTORY):
        for filename in os.listdir(ATTENDANCE_DIRECTORY):
            if filename.endswith('.json'):
                date = filename[:-5]
                with open(os.path.join(ATTENDANCE_DIRECTORY, filename), 'r') as f:
                    data = json.load(f)
                    attendance_data.extend(data)
    
    attendance_data.sort(key=lambda x: (x['date'], x['time']), reverse=True)
    return render_template('attendance.html', attendance=attendance_data)

@app.route('/faces/<filename>')
def serve_face(filename):
    return send_from_directory(FACES_DIRECTORY, filename)

if __name__ == "__main__":
    import os
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
