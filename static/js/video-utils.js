// Video feed utilities - shared between main.js and register.js

// Constants
const MAX_RETRIES = 3;
const STREAM_CHECK_TIMEOUT = 1500;  // Reduced from 2000ms to 1500ms for faster response
const RETRY_DELAY = 800;            // Reduced from 1000ms to 800ms for quicker retries

// Global state variables
let isStreaming = false;
let retryCount = 0;
let checkStream = null;

/**
 * Validates that all required video elements exist
 * @param {string[]} requiredIds - Array of element IDs that must exist
 * @returns {boolean} - true if all elements exist, false otherwise
 */
function validateVideoElements(requiredIds) {
    for (const id of requiredIds) {
        if (!document.getElementById(id)) {
            console.error(`Required element '${id}' not found`);
            return false;
        }
    }
    return true;
}

/**
 * Gets video elements safely with null checks
 * @returns {Object} - Object containing video elements
 */
function getVideoElements() {
    return {
        videoContainer: document.getElementById('videoContainer'),
        videoFeed: document.querySelector('.video-feed'),
        startBtn: document.getElementById('startBtn'),
        stopBtn: document.getElementById('stopBtn'),
        captureBtn: document.getElementById('captureBtn')
    };
}

/**
 * Shows error alert with camera troubleshooting tips
 * @param {string} errorType - Type of error ('loading' or 'streaming')
 */
function showCameraErrorAlert(errorType) {
    const message = errorType === 'streaming' 
        ? 'Camera not responding. Please check your camera connection and permissions.'
        : 'Error loading video feed. Please check:\n\n' +
          '1. Your camera is connected and working\n' +
          '2. Camera permissions are granted in your browser\n' +
          '3. No other application is using the camera\n' +
          '4. Try refreshing the page and allowing camera access\n' +
          '5. If using a laptop, make sure the camera is not covered';
    
    alert(message);
}

/**
 * Resets UI state after stopping video feed
 * @param {Object} elements - Video elements object
 */
function resetVideoUI(elements) {
    const { videoContainer, videoFeed, startBtn, stopBtn, captureBtn } = elements;
    
    if (videoContainer) {
        videoContainer.style.display = 'none';
    }
    if (videoFeed) {
        videoFeed.src = "";
    }
    if (startBtn) {
        startBtn.style.display = 'inline-block';
        startBtn.disabled = false; // Ensure button is enabled and ready to click
    }
    if (stopBtn) {
        stopBtn.style.display = 'none';
        stopBtn.disabled = false; // Reset stop button state
    }
    if (captureBtn) {
        captureBtn.style.display = 'none';
    }
}

/**
 * Starts the video feed with error handling and retry logic
 * @param {boolean} showCaptureButton - Whether to show capture button (for register page)
 */
function startVideoFeed(showCaptureButton = false) {
    const elements = getVideoElements();
    const { videoContainer, videoFeed, startBtn, stopBtn, captureBtn } = elements;
    
    if (!validateVideoElements(['videoContainer', 'startBtn', 'stopBtn'])) {
        return;
    }
    
    if (!videoFeed) {
        console.error('Video feed element not found');
        return;
    }
    
    // Prevent multiple simultaneous start attempts
    if (isStreaming) {
        console.log('Video feed already streaming');
        return;
    }
    
    // Immediately update UI for better responsiveness - prevent button glitching
    if (startBtn) {
        startBtn.disabled = true; // Prevent multiple clicks while starting
        startBtn.style.display = 'none';
    }
    if (stopBtn) {
        stopBtn.style.display = 'inline-block';
        stopBtn.disabled = false; // Ensure stop button is enabled
    }
    if (videoContainer) {
        videoContainer.style.display = 'block';
    }
    if (showCaptureButton && captureBtn) {
        captureBtn.style.display = 'inline-block';
    }
    
    // Set video source with cache-busting timestamp
    const timestamp = new Date().getTime();
    videoFeed.src = '/video_feed?t=' + timestamp;
    
    // Handle video loading errors
    videoFeed.onerror = function() {
        console.error('Error loading video feed');
        
        if (retryCount < MAX_RETRIES) {
            retryCount++;
            console.log(`Retrying video feed (attempt ${retryCount}/${MAX_RETRIES})...`);
            setTimeout(() => startVideoFeed(showCaptureButton), RETRY_DELAY);
        } else {
            showCameraErrorAlert('loading');
            retryCount = 0;
            // Reset UI to initial state on final failure
            stopVideoFeed();
        }
    };
    
    // Check if stream is actually working
    checkStream = setTimeout(() => {
        if (videoFeed.naturalWidth === 0) {
            console.error('Video feed not streaming');
            
            if (retryCount < MAX_RETRIES) {
                retryCount++;
                console.log(`Retrying video feed (attempt ${retryCount}/${MAX_RETRIES})...`);
                setTimeout(() => startVideoFeed(showCaptureButton), RETRY_DELAY);
            } else {
                showCameraErrorAlert('streaming');
                retryCount = 0;
                // Reset UI to initial state on final failure
                stopVideoFeed();
            }
        } else {
            console.log('Video feed streaming successfully');
            retryCount = 0;
            isStreaming = true;
        }
    }, STREAM_CHECK_TIMEOUT);
    
    // Handle successful video loading
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

/**
 * Stops the video feed and releases resources
 */
function stopVideoFeed() {
    const elements = getVideoElements();
    
    // Clear any pending timeouts
    if (checkStream) {
        clearTimeout(checkStream);
        checkStream = null;
    }
    
    // Reset state immediately to prevent button glitching
    isStreaming = false;
    retryCount = 0;
    
    // Update UI immediately for better responsiveness
    resetVideoUI(elements);
    
    // Clear video source to stop the stream immediately
    if (elements.videoFeed) {
        elements.videoFeed.src = "";
        elements.videoFeed.onerror = null;
        elements.videoFeed.onloadeddata = null;
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

/**
 * Gets the current streaming status
 * @returns {boolean} - Current streaming status
 */
function getStreamingStatus() {
    return isStreaming;
}

// Export functions for use in other scripts
window.VideoUtils = {
    startVideoFeed,
    stopVideoFeed,
    getStreamingStatus,
    validateVideoElements,
    getVideoElements
};