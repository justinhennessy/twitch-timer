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
            const container = document.querySelector('.container'); // Updated target

            if (data.timer === -999) {
                timerDisplay.innerText = ""; // Clear the text
                document.getElementById('infiniteSymbol').style.display = 'block'; // Show infinite symbol

                // Remove pulsing classes from container when timer is -999
                container.classList.remove('pulsing-yellow', 'pulsing-red');
                return;  // Exit the function early
            }

            document.getElementById('infiniteSymbol').style.display = 'none'; // Hide the infinite symbol if not in infinite mode

            if (data.timer === -1) {
                timerDisplay.innerText = "Let's Go!";
                container.classList.remove('pulsing-yellow', 'pulsing-red');
                return;
            }

            if (data.timer <= 30 && data.timer > 15) {
                const formattedTime = formatTime(data.timer);
                timerDisplay.innerText = formattedTime;
                container.classList.remove('pulsing-red');
                container.classList.add('pulsing-yellow');
            } else if (data.timer <= 15 && data.timer > 0) {
                const formattedTime = formatTime(data.timer);
                timerDisplay.innerText = formattedTime;
                container.classList.remove('pulsing-yellow');
                container.classList.add('pulsing-red');
            } else if (data.timer === 0) {
                timerDisplay.innerText = 'Time\'s up!';
                container.classList.remove('pulsing-yellow', 'pulsing-red');
                container.style.backgroundColor = 'white';
            } else {
                const formattedTime = formatTime(data.timer);
                timerDisplay.innerText = formattedTime;
                container.classList.remove('pulsing-yellow', 'pulsing-red');
            }
        })
        .catch(error => {
            console.error('Error in displayTimerValue:', error);
            document.getElementById('timerDisplay').innerText = 'Error!';
        });
}

displayTimerValue();
setInterval(displayTimerValue, 1000);
