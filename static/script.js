const counterElement = document.getElementById('counter');
const increaseCounterButton = document.getElementById('increaseCounter');

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
  try {
    const response = await fetch('http://127.0.0.1:5000/timer');
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

async function increaseTimerValue() {
  try {
    const response = await fetch('http://127.0.0.1:5000/add-time', { method: 'POST' });
    if (response.ok) {
      const data = await response.json();
      updateCounter(data.value);
    } else {
      console.error('Error increasing timer value:', response.statusText);
    }
  } catch (error) {
    console.error('Error increasing timer value:', error);
  }
}

setInterval(fetchTimerValue, 1000);
increaseCounterButton.addEventListener('click', increaseTimerValue);

