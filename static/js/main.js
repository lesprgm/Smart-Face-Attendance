// Main page JavaScript - uses shared video utilities

document.addEventListener('DOMContentLoaded', function() {
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    
    if (startBtn) {
        startBtn.addEventListener('click', () => {
            // Only proceed if button is not disabled (simple debouncing)
            if (!startBtn.disabled) {
                VideoUtils.startVideoFeed(false);
            }
        });
    }
    
    if (stopBtn) {
        stopBtn.addEventListener('click', () => {
            // Only proceed if button is not disabled (simple debouncing) 
            if (!stopBtn.disabled) {
                VideoUtils.stopVideoFeed();
            }
        });
    }
});