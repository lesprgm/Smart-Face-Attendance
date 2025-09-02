// Register page JavaScript - handles file upload functionality

/**
 * Handles file upload preview
 * @param {Event} event - File input change event
 */
function handleFileUpload(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.getElementById('uploadPreview') || document.getElementById('imagePreview');
            const uploadedImage = document.getElementById('uploadedImage') || preview;
            
            if (preview) {
                preview.style.display = 'block';
                preview.classList.remove('d-none');
                if (uploadedImage && uploadedImage !== preview) {
                    uploadedImage.src = e.target.result;
                } else if (preview.tagName === 'IMG') {
                    preview.src = e.target.result;
                }
            }
        };
        reader.readAsDataURL(file);
    }
}

/**
 * Handles form submission for face registration
 * @param {Event} event - Form submit event
 */
function handleUploadSubmit(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    const submitBtn = form.querySelector('button[type="submit"]');
    
    if (!submitBtn) {
        console.error('Submit button not found');
        return;
    }
    
    const originalText = submitBtn.textContent;
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
        submitBtn.textContent = originalText;
    });
}

// Only initialize if elements exist (for compatibility with different register page versions)
document.addEventListener('DOMContentLoaded', function() {
    // File upload handling
    const imageFile = document.getElementById('imageFile') || document.getElementById('image');
    if (imageFile) {
        imageFile.addEventListener('change', handleFileUpload);
    }

    // Form submission handling
    const uploadForm = document.getElementById('uploadForm') || document.getElementById('registerForm');
    if (uploadForm) {
        uploadForm.addEventListener('submit', handleUploadSubmit);
    }
    
    // Video functionality (if elements exist for advanced register page)
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const captureBtn = document.getElementById('captureBtn');
    
    // Add debouncing for video buttons
    let isProcessing = false;

    if (startBtn && window.VideoUtils) {
        startBtn.addEventListener('click', () => {
            if (!isProcessing) {
                isProcessing = true;
                VideoUtils.startVideoFeed(true);
                setTimeout(() => { isProcessing = false; }, 1000);
            }
        });
    }

    if (stopBtn && window.VideoUtils) {
        stopBtn.addEventListener('click', () => {
            if (!isProcessing) {
                isProcessing = true;
                VideoUtils.stopVideoFeed();
                setTimeout(() => { isProcessing = false; }, 500);
            }
        });
    }

    if (captureBtn && window.VideoUtils) {
        captureBtn.addEventListener('click', function() {
            if (!VideoUtils.getStreamingStatus()) {
                alert('Please start the video feed first');
                return;
            }

            captureBtn.disabled = true;
            captureBtn.textContent = 'Capturing...';

            fetch('/capture')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const previewContainer = document.getElementById('previewContainer');
                        const previewImage = document.getElementById('previewImage');
                        if (previewContainer && previewImage) {
                            previewContainer.style.display = 'block';
                            previewImage.src = data.image_url;
                        }
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
        });
    }
});