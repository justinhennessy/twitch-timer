// Set the default start time to 5 minutes (300 seconds)
let timeRemaining = 300;
let paused = false;

// Update the timer on the page
function updateTimer() {
    let minutes = Math.floor(timeRemaining / 60);
    let seconds = timeRemaining % 60;
    document.getElementById('timer').textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
}

// Countdown function
function countdown() {
    if (!paused && timeRemaining > 0) {
        timeRemaining--;
        updateTimer();
    } else if (timeRemaining === 0) {
        clearInterval(interval);
        document.getElementById('timer').textContent = 'Jam Ended!';
    }
}

// Start the countdown timer
let interval = setInterval(countdown, 1000);

function addTime() {
    fetch('/add-time', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ seconds: 30 })
    })
    .then(response => response.json())
    .then(data => {
        timeRemaining = data.timeRemaining;
        updateTimer();
    })
    .catch(error => {
        console.error(error);
    });
}


// Subtract 30 seconds from the timer, ensuring it does not go below 0
function subtractTime() {
    timeRemaining = Math.max(0, timeRemaining - 30);
    updateTimer();
}

// Toggle pause and resume
function togglePauseResume() {
    paused = !paused;
    document.getElementById('pauseResume').textContent = paused ? 'Resume' : 'Pause';
}

// Reset the timer to 5 minutes
function resetTime() {
    timeRemaining = 300;
    updateTimer();
    clearInterval(interval);
    interval = setInterval(countdown, 1000);
}

// Add event listeners for the buttons
document.getElementById('addTime').addEventListener('click', addTime);
document.getElementById('subtractTime').addEventListener('click', subtractTime);
document.getElementById('pauseResume').addEventListener('click', togglePauseResume);
document.getElementById('resetTime').addEventListener('click', resetTime);

// Add event listener for color picker
document.getElementById('colorPicker').addEventListener('input', function() {
    const newColor = this.value;
    document.getElementById('timer').style.color = newColor;
});
