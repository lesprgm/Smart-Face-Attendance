import face_recognition
import os, sys
import cv2
import numpy as np
import math

# Constants
FACE_MATCH_THRESHOLD = 0.6
FRAME_RESIZE_FACTOR = 0.25
FRAME_SCALE_FACTOR = 4
RECTANGLE_COLOR = (0, 0, 255)
RECTANGLE_THICKNESS = 2
TEXT_COLOR = (255, 255, 255)
TEXT_SCALE = 0.8

def face_confidence(face_distance, face_match_threshold=FACE_MATCH_THRESHOLD):
    range = (1.0 - face_match_threshold)
    linear_val = (1.0 - face_distance) / (range * 2.0)
    
    if face_distance > face_match_threshold:
        return str(round(linear_val * 100, 2)) + '%'
    else:
        value = (linear_val +((1.0 - linear_val)* math.pow((linear_val - 0.5) * 2, 0.2))) * 100
        return str(round(value, 2)) + '%'
 
class FaceRecognition:
    face_locations = []
    face_encodings = []
    face_names = []
    known_face_encodings =[]
    known_face_names = []
    process_current_frame = True
    
    def __init__(self):
        self.encode_faces()

    
    def encode_faces(self):
        for image in os.listdir('faces'):
            if image.endswith(('.jpg', '.jpeg', '.png')):  # Filter by image extensions
                face_image = face_recognition.load_image_file(f'faces/{image}')
                face_encodings = face_recognition.face_encodings(face_image)
                
                if face_encodings:  # Check if face encodings exist
                    face_encoding = face_encodings[0]
                    self.known_face_encodings.append(face_encoding)
                    self.known_face_names.append(os.path.splitext(image)[0])  # Remove extension from name
                else:
                    print(f"No face detected in {image}")
            
        print(self.known_face_names)

    def run_recognition(self):
        video_capture = cv2.VideoCapture(0)
        
        if not video_capture.isOpened():
            sys.exit("Video source cannot found...")
            
        while True:
            ret, frame = video_capture.read()
            
            if self.process_current_frame:
                small_frame = cv2.resize(frame, (0, 0), fx=FRAME_RESIZE_FACTOR, fy=FRAME_RESIZE_FACTOR)
                rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                
                
                self.face_locations =face_recognition.face_locations(rgb_small_frame)
                self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)
                
                self.face_names = []
                for face_encoding in self.face_encodings:
                    matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                    name = 'Unknown'
                    confidence = 'Unknown'
                    
                    face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    
                    if matches[best_match_index]:
                        name = self.known_face_names[best_match_index]
                        confidence = face_confidence(face_distances[best_match_index])
                        
                    self.face_names.append(f'{name} ({confidence})')
                    
            self.process_current_frame = not self.process_current_frame
            
            
            for(top, right, bottom ,left), name in zip(self.face_locations, self.face_names):
                top *= FRAME_SCALE_FACTOR
                right *= FRAME_SCALE_FACTOR
                bottom *= FRAME_SCALE_FACTOR
                left *= FRAME_SCALE_FACTOR
                
                cv2.rectangle(frame, (left, top), (right, bottom), RECTANGLE_COLOR, RECTANGLE_THICKNESS)
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), RECTANGLE_COLOR, -1)
                cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, TEXT_SCALE, TEXT_COLOR, 1)
                
            cv2.imshow('Face Recognition', frame)
            
            if cv2.waitKey(1) == ord('q'):
                break
        
        video_capture.release()
        cv2.destroyAllWindows()
                      

if __name__ == '__main__':
    fr = FaceRecognition()
    fr.run_recognition()
    