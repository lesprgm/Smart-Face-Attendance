let isStreaming = false;
let retryCount = 0;
let checkStream = null; // Declare at global scope so stopVideoFeed can access it
const MAX_RETRIES = 3;

function startVideoFeed() {
    const videoContainer = document.getElementById('videoContainer');
    const videoFeed = document.querySelector('.video-feed');
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    
    videoContainer.style.display = 'block';
    startBtn.style.display = 'none';
    stopBtn.style.display = 'inline-block';
    
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
            stopBtn.style.display = 'none';
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
                stopBtn.style.display = 'none';
            }
        } else {
            console.log('Video streaming successfully');
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
    
    // Clear any pending timeouts
    if (checkStream) {
        clearTimeout(checkStream);
        checkStream = null;
    }
    
    // Hide video container and clear video source
    videoContainer.style.display = 'none';
    videoFeed.src = "";
    isStreaming = false;
    retryCount = 0;
    
    // Reset button states
    startBtn.style.display = 'inline-block';
    stopBtn.style.display = 'none';
    
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

document.addEventListener('DOMContentLoaded', function() {
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    
    startBtn.addEventListener('click', startVideoFeed);
    stopBtn.addEventListener('click', stopVideoFeed);
}); 