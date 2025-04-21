document.addEventListener('DOMContentLoaded', function() {
    const acceptBtn = document.getElementById('acceptBtn');
    const prefBtn = document.getElementById('prefBtn');
    
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
    
    prefBtn.addEventListener('click', function() {
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