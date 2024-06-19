let baseUrl;
let timerUuid;

document.addEventListener('DOMContentLoaded', (event) => {
    fetch('/api/base_url')
        .then(response => response.json())
        .then(data => {
            baseUrl = data.base_url;
            const urlParams = new URLSearchParams(window.location.search);
            timerUuid = urlParams.get('uuid');
            if (timerUuid) {
                displayTimerInfo(timerUuid);
                document.getElementById('docsLink').href = `${baseUrl}/documentation.html?uuid=${timerUuid}`;
            }
        });
});

function displayTimerInfo(uuid) {
    const timerInfoDiv = document.getElementById('timerInfo');
    timerInfoDiv.innerHTML = `
        <p>Your unique timer URL: <a href="${baseUrl}/timer.html?uuid=${uuid}" target="_blank">${baseUrl}/timer.html?uuid=${uuid}</a></p>
    `;
}

function updateConfig() {
    const defaultTime = document.getElementById('defaultTime').value;
    fetch(`${baseUrl}/api/update_config/${timerUuid}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ default_time: defaultTime })
    })
    .then(response => response.json())
    .then(data => {
        alert('Configuration updated!');
    })
    .catch(error => console.error('Error:', error));
}
