document.addEventListener('DOMContentLoaded', function() {
    const acceptBtn = document.getElementById('acceptBtn');
    const prefBtn = document.getElementById('prefBtn');
    
    // Handle accept button click
    acceptBtn.addEventListener('click', function() {
        fetch('/set_privacy_notice', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.href = '/';
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
    
    // Handle preferences button click
    prefBtn.addEventListener('click', function() {
        // For now, just accept and proceed
        fetch('/set_privacy_notice', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.href = '/';
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
}); 