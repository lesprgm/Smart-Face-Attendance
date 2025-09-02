// Main page JavaScript - uses shared video utilities

document.addEventListener('DOMContentLoaded', function() {
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    
    // Add debouncing to prevent rapid button clicks
    let isProcessing = false;
    
    if (startBtn) {
        startBtn.addEventListener('click', () => {
            if (!isProcessing) {
                isProcessing = true;
                VideoUtils.startVideoFeed(false);
                // Reset processing flag after a short delay
                setTimeout(() => { isProcessing = false; }, 1000);
            }
        });
    }
    
    if (stopBtn) {
        stopBtn.addEventListener('click', () => {
            if (!isProcessing) {
                isProcessing = true;
                VideoUtils.stopVideoFeed();
                // Reset processing flag after a short delay
                setTimeout(() => { isProcessing = false; }, 500);
            }
        });
    }
});