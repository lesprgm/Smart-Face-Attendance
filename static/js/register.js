let isStreaming = false;
let retryCount = 0;
let checkStream = null; // Declare at global scope so stopVideoFeed can access it
const MAX_RETRIES = 3;

function startVideoFeed() {
    const videoContainer = document.getElementById('videoContainer');
    const videoFeed = document.querySelector('.video-feed');
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const captureBtn = document.getElementById('captureBtn');
    
    if (!videoContainer || !videoFeed || !startBtn || !stopBtn) {
        console.error('Required video elements not found');
        return;
    }
    
    videoContainer.style.display = 'block';
    startBtn.style.display = 'none';
    stopBtn.style.display = 'inline-block';
    if (captureBtn) {
        captureBtn.style.display = 'inline-block';
    }
    
    const timestamp = new Date().getTime();
    videoFeed.src = '/video_feed?t=' + timestamp;
    
    videoFeed.onerror = function() {
        console.error('Error loading video feed');
        stopVideoFeed();
        
        if (retryCount < MAX_RETRIES) {
            retryCount++;
            console.log(`Retrying video feed (attempt ${retryCount}/${MAX_RETRIES})...`);
            setTimeout(startVideoFeed, 1000);
        } else {
            alert('Error loading video feed. Please check:\n\n' +
                  '1. Your camera is connected and working\n' +
                  '2. Camera permissions are granted in your browser\n' +
                  '3. No other application is using the camera\n' +
                  '4. Try refreshing the page and allowing camera access\n' +
                  '5. If using a laptop, make sure the camera is not covered');
            retryCount = 0;
            startBtn.style.display = 'inline-block';
        }
    };
    
    checkStream = setTimeout(() => {
        if (videoFeed.naturalWidth === 0) {
            console.error('Video feed not streaming');
            stopVideoFeed();
            
            if (retryCount < MAX_RETRIES) {
                retryCount++;
                console.log(`Retrying video feed (attempt ${retryCount}/${MAX_RETRIES})...`);
                setTimeout(startVideoFeed, 1000);
            } else {
                alert('Camera not responding. Please check your camera connection and permissions.');
                retryCount = 0;
                startBtn.style.display = 'inline-block';
            }
        } else {
            console.log('Video feed streaming successfully');
            retryCount = 0;
            isStreaming = true;
        }
    }, 2000);
    
    videoFeed.onloadeddata = function() {
        if (checkStream) {
            clearTimeout(checkStream);
            checkStream = null;
        }
        console.log('Video feed loaded successfully');
        retryCount = 0;
        isStreaming = true;
    };
}

function stopVideoFeed() {
    const videoContainer = document.getElementById('videoContainer');
    const videoFeed = document.querySelector('.video-feed');
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const captureBtn = document.getElementById('captureBtn');
    
    // Clear any pending timeouts
    if (checkStream) {
        clearTimeout(checkStream);
        checkStream = null;
    }
    
    if (videoContainer) {
        videoContainer.style.display = 'none';
    }
    if (videoFeed) {
        videoFeed.src = "";
    }
    isStreaming = false;
    retryCount = 0;
    
    if (startBtn) {
        startBtn.style.display = 'inline-block';
    }
    if (stopBtn) {
        stopBtn.style.display = 'none';
    }
    if (captureBtn) {
        captureBtn.style.display = 'none';
    }
    
    // Call backend to properly release camera resources
    fetch('/stop_video_feed', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Video feed stopped successfully');
        } else {
            console.error('Error stopping video feed:', data.error);
        }
    })
    .catch(error => {
        console.error('Error calling stop video feed:', error);
    });
}

/*function captureImage() {
    if (!isStreaming) {
        alert('Please start the video feed first');
        return;
    }

    const captureBtn = document.getElementById('captureBtn');
    captureBtn.disabled = true;
    captureBtn.textContent = 'Capturing...';

    fetch('/capture')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const previewContainer = document.getElementById('previewContainer');
                previewContainer.style.display = 'block';
                document.getElementById('previewImage').src = data.image_url;
            } else {
                alert('Failed to capture image: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error capturing image:', error);
            alert('Error capturing image. Please try again.');
        })
        .finally(() => {
            captureBtn.disabled = false;
            captureBtn.textContent = 'Capture Image';
        });
}*/

function handleFileUpload(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.getElementById('uploadPreview');
            const uploadedImage = document.getElementById('uploadedImage');
            preview.style.display = 'block';
            uploadedImage.src = e.target.result;
        };
        reader.readAsDataURL(file);
    }
}

function handleUploadSubmit(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const submitBtn = form.querySelector('button[type="submit"]');
    
    submitBtn.disabled = true;
    submitBtn.textContent = 'Registering...';

    fetch('/register', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Face registered successfully!');
            window.location.href = '/';
        } else {
            alert('Registration failed: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error registering face:', error);
        alert('Error registering face. Please try again.');
    })
    .finally(() => {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Register Face';
    });
}

document.addEventListener('DOMContentLoaded', function() {
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const captureBtn = document.getElementById('captureBtn');
    const imageFile = document.getElementById('imageFile');
    const uploadForm = document.getElementById('uploadForm');

    if (startBtn) {
        startBtn.addEventListener('click', startVideoFeed);
    }

    if (stopBtn) {
        stopBtn.addEventListener('click', stopVideoFeed);
    }


    if (imageFile) {
        imageFile.addEventListener('change', handleFileUpload);
    }

    if (uploadForm) {
        uploadForm.addEventListener('submit', handleUploadSubmit);
    }
}); 