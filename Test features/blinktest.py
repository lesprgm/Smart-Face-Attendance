import cv2
import dlib
import imutils

from scipy.spatial import distance as dist

from imutils import face_utils

#cam = cv2.VideoCapture('test video/my_blink.mp4')
cam = cv2.VideoCapture(0)


def calculate_EAR(eye):
    
    y1 = dist.euclidean(eye[1], eye[5])
    y2 = dist.euclidean(eye[2], eye[4])
    
    x1 = dist.euclidean(eye[0], eye[3])
    
    EAR = (y1+y2)/x1 # x1 *2
    return EAR


blink_threshold = 0.45
consecutive_frames = 3 
count_frame = 0

(L_start, L_end) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(R_start, R_end) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]    
    

detector = dlib.get_frontal_face_detector() 
landmark_predict = dlib.shape_predictor( 
    'Model/shape_predictor_68_face_landmarks.dat') 

while 1:
    
    #if cam.get(cv2.CAP_PROP_POS_FRAMES) == cam.get(
            #cv2.CAP_PROP_FRAME_COUNT):
        #cam.set(cv2.CAP_PROP_POS_FRAMES, 0)
    #else:
        ret, frame = cam.read()
        #frame = imutils.resize(frame, width = 640)
        frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        
        img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        faces = detector(img_gray)
        for face in faces:
            shape = landmark_predict(img_gray, face)
            
            shape = face_utils.shape_to_np(shape)
            
            lefteye = shape[L_start: L_end] 
            righteye = shape[R_start:R_end] 
            
            left_EAR = calculate_EAR(lefteye) 
            right_EAR = calculate_EAR(righteye) 
            
            avg = (left_EAR + right_EAR) /2
            if avg < blink_threshold:
                count_frame += 1
            else:
                if count_frame >= consecutive_frames:
                    cv2.putText(frame, 'Liveness Detected', (30, 30),
                                cv2.FONT_HERSHEY_DUPLEX, 1, (0,200,0), 1)
                else:
                    count_frame = 0
            
        cv2.imshow('Camera Feed', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
cam.release()
