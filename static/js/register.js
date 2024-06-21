let baseUrl;
let userEmail;

document.addEventListener('DOMContentLoaded', (event) => {
    fetch('/api/base_url')
        .then(response => response.json())
        .then(data => {
            baseUrl = data.base_url;
        });

    // Check if the user is logged in and has an email stored in the session
    fetch('/api/user_info')
        .then(response => response.json())
        .then(data => {
            if (data.email) {
                userEmail = data.email;
                document.getElementById('email').value = userEmail;
                document.getElementById('googleLogin').style.display = 'none';
                document.getElementById('emailLogin').classList.remove('hidden');
            }
        });
});

document.getElementById('registerForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const email = userEmail || document.getElementById('email').value;
    fetch(baseUrl + '/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email })
    })
    .then(response => response.json())
    .then(data => {
        const timerUuid = data.uuid;
        window.location.href = `${baseUrl}/personal_timer.html?uuid=${timerUuid}`;
    });
});

function showEmailLogin() {
    document.getElementById('emailLogin').classList.remove('hidden');
    document.getElementById('googleLogin').style.display = 'none';
}
