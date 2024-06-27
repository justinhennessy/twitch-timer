const baseUrl = '/api';

function fetchTimers() {
    fetch(`${baseUrl}/timers_status`)
        .then(response => response.json())
        .then(data => {
            const timersBody = document.getElementById('timersBody');
            timersBody.innerHTML = '';

            if (data.timers.length === 0) {
                const noTimersMessage = document.createElement('tr');
                noTimersMessage.innerHTML = `<td colspan="7" style="text-align: center;">There are currently no timers on the platform</td>`;
                timersBody.appendChild(noTimersMessage);
            } else {
                data.timers.forEach(timer => {
                    const row = document.createElement('tr');
                    row.classList.add(timer.is_active ? 'active' : 'inactive');
                    row.innerHTML = `
                        <td>${timer.email}</td>
                        <td><a href="/timer.html?uuid=${timer.uuid}" target="_blank">${timer.uuid}</a></td>
                        <td>${timer.last_viewed || 'Never'}</td>
                        <td class="status" data-uuid="${timer.uuid}">${timer.is_active ? 'Active' : 'Inactive'}</td>
                        <td id="getCount-${timer.uuid}">${timer.get_count || 0}</td>
                        <td id="setCount-${timer.uuid}">${timer.set_count || 0}</td>
                        <td>
                            <i class="fas fa-play" onclick="startTimer('${timer.uuid}')" title="Start Timer"></i>
                            <i class="fas fa-redo" onclick="resetTimer('${timer.uuid}')" title="Reset Timer"></i>
                            <i class="fas fa-trash-alt" onclick="deleteTimer('${timer.uuid}')" title="Delete Timer"></i>
                        </td>
                    `;
                    timersBody.appendChild(row);
                });
                attachEventListeners();
            }
        }).catch(error => console.error('Error fetching timers:', error));
}

function attachEventListeners() {
    document.querySelectorAll('.status').forEach(statusCell => {
        statusCell.addEventListener('mouseenter', showTooltip);
        statusCell.addEventListener('mouseleave', hideTooltip);
    });
}

function startTimer(uuid) {
    fetch(`${baseUrl}/start/${uuid}`)
        .then(response => response.json())
        .then(() => {
            fetchTimers();
        }).catch(error => console.error('Error starting timer:', error));
}

function resetTimer(uuid) {
    fetch(`${baseUrl}/reset/${uuid}`)
        .then(response => response.json())
        .then(() => {
            fetchTimers();
        }).catch(error => console.error('Error resetting timer:', error));
}

function deleteTimer(uuid) {
    if (confirm('Are you sure you want to delete this timer?')) {
        fetch(`${baseUrl}/delete/${uuid}`, { method: 'DELETE' })
            .then(response => response.json())
            .then(() => {
                fetchTimers();
                fetchRedisCallCounts(); // Fetch updated Redis call counts after deleting a timer
            }).catch(error => console.error('Error deleting timer:', error));
    }
}

function showTooltip(event) {
    const status = event.target.innerText;
    const uuid = event.target.getAttribute('data-uuid');
    if (status === 'Active') {
        fetch(`${baseUrl}/timer/${uuid}`)
            .then(response => response.json())
            .then(data => {
                const tooltip = document.getElementById('tooltip');
                tooltip.innerText = `Current Timer Value: ${data.timer}`;
                tooltip.style.display = 'block';
                tooltip.style.left = `${event.pageX + 10}px`;
                tooltip.style.top = `${event.pageY - 30}px`;  // Position above the cursor
            }).catch(error => console.error('Error showing tooltip:', error));
    }
}

function hideTooltip() {
    const tooltip = document.getElementById('tooltip');
    tooltip.style.display = 'none';
}

function fetchRedisCallCounts() {
    fetch(`${baseUrl}/redis_operations`)
        .then(response => response.json())
        .then(data => {
            const getCountElement = document.getElementById('getCount');
            const setCountElement = document.getElementById('setCount');

            getCountElement.textContent = data['GET:timer_update'] || 0;
            setCountElement.textContent = data['SET:timer_update'] || 0;

            // Optionally, update more detailed elements here
        }).catch(error => console.error('Error fetching Redis call counts:', error));
}

document.addEventListener('DOMContentLoaded', () => {
    fetchTimers();
    fetchRedisCallCounts();
    setInterval(fetchTimers, 5000); // Update timer data every 5 seconds
    setInterval(fetchRedisCallCounts, 5000); // Update Redis call counts every 5 seconds
});
