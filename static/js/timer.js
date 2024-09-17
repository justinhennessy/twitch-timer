function formatTime(seconds) {
    const min = Math.floor(seconds / 60);
    const sec = seconds % 60;
    return `${min}:${sec < 10 ? '0' : ''}${sec}`;
}

function displayTimerValue() {
    const urlParams = new URLSearchParams(window.location.search);
    const uuid = urlParams.get('uuid');

    if (!uuid) {
        document.getElementById('timerDisplay').innerText = 'No timer specified!';
        return;
    }

    fetch(`/api/timer/${uuid}`)
        .then(response => response.json())
        .then(data => {
            const timerDisplay = document.getElementById('timerDisplay');
            const body = document.body;

            if (data.timer === -999) {
                timerDisplay.innerText = ""; // Clear the text
                document.getElementById('infiniteSymbol').style.display = 'block'; // Show infinite symbol

                // Remove background animation class when timer is -999
                body.classList.remove('pulsing-yellow', 'pulsing-red');
                return;  // Exit the function early
            }

            document.getElementById('infiniteSymbol').style.display = 'none'; // Hide the infinite symbol if not in infinite mode

            if (data.timer === -1) {
                timerDisplay.innerText = "Let's Go!";
                body.classList.remove('pulsing-yellow', 'pulsing-red');
                return;
            }

            if (data.timer <= 30 && data.timer > 15) {
                const formattedTime = formatTime(data.timer);
                timerDisplay.innerText = formattedTime;
                body.classList.remove('pulsing-red');
                body.classList.add('pulsing-yellow');
            } else if (data.timer <= 15 && data.timer > 0) {
                const formattedTime = formatTime(data.timer);
                timerDisplay.innerText = formattedTime;
                body.classList.remove('pulsing-yellow');
                body.classList.add('pulsing-red');
            } else if (data.timer === 0) {
                timerDisplay.innerText = 'Times up!';
                body.classList.remove('pulsing-yellow', 'pulsing-red');
                body.style.backgroundColor = 'white';
            } else {
                const formattedTime = formatTime(data.timer);
                timerDisplay.innerText = formattedTime;
                body.classList.remove('pulsing-yellow', 'pulsing-red');
            }
        })
        .catch(error => {
            console.error('Error in displayTimerValue:', error);
            document.getElementById('timerDisplay').innerText = 'Error!';
        });
}

displayTimerValue();
setInterval(displayTimerValue, 1000);
