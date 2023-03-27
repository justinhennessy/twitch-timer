const counterElement = document.getElementById('counter');

function formatTime(seconds) {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.round(seconds % 60);
  return `${String(minutes).padStart(2, '0')}:${String(remainingSeconds).padStart(2, '0')}`;
}

function updateCounter(value) {
  if (value <= 0) {
    counterElement.textContent = "Next Jam";
  } else {
    counterElement.textContent = formatTime(value);
  }
}

async function fetchTimerValue() {
  console.log('fetchTimerValue called');
  try {
    const response = await fetch('https://twitch-timer.herokuapp.com/timer');
    if (response.ok) {
      const data = await response.json();
      updateCounter(data.value);
    } else {
      console.error('Error fetching timer value:', response.statusText);
    }
  } catch (error) {
    console.error('Error fetching timer value:', error);
  }
}

setInterval(fetchTimerValue, 1000);
