// Main page JavaScript - uses shared video utilities

document.addEventListener('DOMContentLoaded', function() {
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    
    if (startBtn) {
        startBtn.addEventListener('click', () => VideoUtils.startVideoFeed(false));
    }
    
    if (stopBtn) {
        stopBtn.addEventListener('click', VideoUtils.stopVideoFeed);
    }
}); 