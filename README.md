# 📘 Face Recognition Attendance System

A Flask-based web application for real-time **student attendance tracking** using **face recognition**. Users can register faces, detect and recognize them live via webcam, and view attendance history, all from a modern web interface.

---

##  Features

- Real-time face detection via webcam
-  Face recognition using `face_recognition` (built on dlib)
-  Easy face registration with image preview
-  Attendance records with timestamps
-  View all registered faces
-  Privacy notice page to inform users about data usage
-  Responsive Bootstrap UI with modern design

---

## Folder Structure

```
├── app.py                     # Flask backend
├── face_recognition_system.py # Face recognition logic
├── templates/
│   ├── index.html            # Home page with live feed
│   ├── register.html         # Face registration form
│   ├── view_faces.html       # List of registered faces
│   ├── attendance.html       # View attendance records
│   └── privacy_notice.html   # Privacy notice popup
├── static/
│   ├── css/                  # CSS stylesheets
│   ├── js/                   # JavaScript files
│   └── attendance/           # Attendance-related static files
├── faces/                    # Stores uploaded face images
├── screenshots/              # Project screenshots
├── Model/                    # Model files
├── dlib/                     # dlib library files
├── requirements.txt          # Python dependencies
├── Dockerfile               # Docker configuration
├── Procfile                 # Heroku configuration
└── LICENSE                  # Project license
```

---

## ⚙️ Tech Stack

- **Python 3.10+**
- **Flask** – Web server
- **Gunicorn** – Production WSGI server
- **face_recognition** – Core face recognition engine
- **OpenCV** (headless) – Image capture and processing
- **NumPy** – Numerical computing
- **Pandas** – Data manipulation and analysis
- **Bootstrap 5** – Frontend styling

---

## 🛠️ Setup Instructions

### 🔧 1. Clone the Repository

```bash
git clone https://github.com/lesprgm/face-attendance-app.git
cd face-attendance-app
```

### 🐍 2. Set Up Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 📦 3. Install Requirements

```bash
pip install -r requirements.txt
```

If you face issues with `dlib`, make sure you have:
- CMake
- Boost
- GCC or Clang (on Mac/Linux)

### ▶️ 4. Run the App Locally

```bash
python app.py
```

Then open your browser and visit:  
**`http://127.0.0.1:5000`**

---

## 📸 Functional Routes

| Route                | Description                                    |
|---------------------|------------------------------------------------|
| `/`                 | Home page with live camera feed                |
| `/privacy_notice`   | Privacy notice page (required before access)   |
| `/set_privacy_notice` | API endpoint to accept privacy notice         |
| `/video_feed`       | Live video stream endpoint                     |
| `/register`         | Upload image and name to register face         |
| `/view_faces`       | View all registered faces                      |
| `/attendance`       | View attendance records                        |
| `/faces/<filename>` | Serve registered face images                   |

---

## Privacy by Design

- Users are informed via a **dedicated privacy notice**
- No images are stored permanently without consent
- You can use a sample image (e.g., of Ronaldo) to test safely

---

## 🖼️ Screenshots



### Homepage
![Homepage Screenshot](screenshots/Homepage.jpg)

### Register Face
![Register Face](screenshots/Register.jpg)

### Attendance View
![Attendance View](screenshots/Attendance.jpg)

### Faces View
![Faces View](screenshots/Faces.jpg)

---

##  Known Issues

This project may have unresolved bugs or limitations.  
Please refer to the **[Issues](../../issues)** section of this repository for up-to-date details or to report new problems.

---

##  Credits

Developed by **Leslie Osei-Anane**  
Face Recognition Tutorial: (https://youtu.be/tl2eEBFEHqM?si=WZ4n19KU4zxzTZ91)  
GitHub: [@lesprgm](https://github.com/lesprgm)