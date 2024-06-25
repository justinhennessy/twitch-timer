const baseUrl = '/api';

function fetchTimers() {
    fetch(`${baseUrl}/timers_status`)
        .then(response => response.json())
        .then(data => {
            const timersBody = document.getElementById('timersBody');
            timersBody.innerHTML = '';

            if (data.timers.length === 0) {
                const noTimersMessage = document.createElement('tr');
                noTimersMessage.innerHTML = `
                    <td colspan="7" style="text-align: center;">There are currently no timers on the platform</td>
                `;
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
                        <td id="getCount-${timer.uuid}">${timer.get_count}</td>
                        <td id="setCount-${timer.uuid}">${timer.set_count}</td>
                        <td>
                            <i class="fas fa-play" onclick="startTimer('${timer.uuid}')" title="Start Timer"></i>
                            <i class="fas fa-redo" onclick="resetTimer('${timer.uuid}')" title="Reset Timer"></i>
                            <i class="fas fa-trash-alt" onclick="deleteTimer('${timer.uuid}')" title="Delete Timer"></i>
                        </td>
                    `;
                    timersBody.appendChild(row);
                });

                // Add hover event listeners
                document.querySelectorAll('.status').forEach(statusCell => {
                    statusCell.addEventListener('mouseenter', showTooltip);
                    statusCell.addEventListener('mouseleave', hideTooltip);
                });
            }
        });
}

function startTimer(uuid) {
    fetch(`${baseUrl}/start/${uuid}`)
        .then(response => response.json())
        .then(() => {
            fetchTimers();
        });
}

function resetTimer(uuid) {
    fetch(`${baseUrl}/reset/${uuid}`)
        .then(response => response.json())
        .then(() => {
            fetchTimers();
        });
}

function deleteTimer(uuid) {
    if (confirm('Are you sure you want to delete this timer?')) {
        fetch(`${baseUrl}/delete/${uuid}`, { method: 'DELETE' })
            .then(response => response.json())
            .then(() => {
                fetchTimers();
                fetchRedisCallCounts(); // Fetch updated Redis call counts after deleting a timer
            });
    }
}

function showTooltip(event) {
    const status = event.target.innerText;
    if (status === 'Active') {
        const uuid = event.target.getAttribute('data-uuid');
        fetch(`${baseUrl}/timer/${uuid}`)
            .then(response => response.json())
            .then(data => {
                const tooltip = document.getElementById('tooltip');
                tooltip.innerText = `Current Timer Value: ${data.timer}`;
                tooltip.style.display = 'block';
                tooltip.style.left = `${event.pageX + 10}px`;
                tooltip.style.top = `${event.pageY - 30}px`;  // Position above the cursor
            });
    }
}

function hideTooltip() {
    const tooltip = document.getElementById('tooltip');
    tooltip.style.display = 'none';
}

document.addEventListener('DOMContentLoaded', (event) => {
    fetchTimers();
    fetchRedisCallCounts();
    setInterval(fetchTimers, 5000); // Update timer data every 5 seconds
    setInterval(fetchRedisCallCounts, 5000); // Update Redis call counts every 5 seconds
});
