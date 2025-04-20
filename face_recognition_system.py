import face_recognition
import cv2
import numpy as np
from datetime import datetime
import os

class FaceRecognitionSystem:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.attendance_records = []
        self.last_attendance_check = {}  
        self.load_known_faces()

    def load_known_faces(self):
        self.known_face_encodings = []
        self.known_face_names = []
        
        if not os.path.exists('faces'):
            os.makedirs('faces')
        
        for image in os.listdir('faces'):
            if image.endswith(('.jpg', '.jpeg', '.png')):
                face_image = face_recognition.load_image_file(f'faces/{image}')
                face_encoding = face_recognition.face_encodings(face_image)
                if face_encoding:
                    self.known_face_encodings.append(face_encoding[0])
                    self.known_face_names.append(os.path.splitext(image)[0])
        
        print(f"Loaded {len(self.known_face_names)} known faces")

    def process_frame(self, frame):
        if len(self.known_face_encodings) == 0:
            return frame

        
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            name = "Unknown"
            
            if True in matches:
                first_match_index = matches.index(True)
                name = self.known_face_names[first_match_index]
                
                current_time = datetime.now()
                if name not in self.last_attendance_check or \
                   (current_time - self.last_attendance_check[name]).total_seconds() > 30:  
                    self.attendance_records.append({
                        'name': name,
                        'time': current_time.strftime('%Y-%m-%d %H:%M:%S')
                    })
                    self.last_attendance_check[name] = current_time
            
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), -1)
            cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)
        
        return frame

    def get_attendance_records(self):
        return sorted(self.attendance_records, 
                    key=lambda x: datetime.strptime(x['time'], '%Y-%m-%d %H:%M:%S'),
                    reverse=True)

    def register_face(self, image_path, name):
        if not os.path.exists('faces'):
            os.makedirs('faces')
        
        filename = f"{name}.jpg"
        file_path = os.path.join('faces', filename)
        cv2.imwrite(file_path, cv2.imread(image_path))
        
        self.load_known_faces()
        return True 