from flask import Flask, request, jsonify

app = Flask(__name__)

# Set the default start time to 5 minutes (300 seconds)
time_remaining = 300
paused = False

# Update the timer
def update_timer():
    minutes = time_remaining // 60
    seconds = time_remaining % 60
    timer_text = f"{minutes:02d}:{seconds:02d}"
    return timer_text

# Countdown function
def countdown():
    global time_remaining
    if not paused and time_remaining > 0:
        time_remaining -= 1
        return update_timer()
    elif time_remaining == 0:
        return 'Jam Ended!'

# Add 30 seconds to the timer
@app.route('/add-time', methods=['POST'])
def add_time():
    global time_remaining
    data = request.get_json()
    seconds = data.get('seconds', 0)
    time_remaining += seconds
    return jsonify({'timeRemaining': time_remaining})

# Subtract 30 seconds from the timer, ensuring it does not go below 0
@app.route('/subtract-time', methods=['POST'])
def subtract_time():
    global time_remaining
    data = request.get_json()
    seconds = data.get('seconds', 0)
    time_remaining = max(0, time_remaining - seconds)
    return jsonify({'timeRemaining': time_remaining})

# Toggle pause and resume
@app.route('/toggle-pause', methods=['POST'])
def toggle_pause():
    global paused
    paused = not paused
    return jsonify({'paused': paused})

# Reset the timer to 5 minutes
@app.route('/reset-time', methods=['POST'])
def reset_time():
    global time_remaining
    time_remaining = 300
    return jsonify({'timeRemaining': time_remaining})

# Get the current timer value
@app.route('/get-timer', methods=['GET'])
def get_timer():
    return jsonify({'timeRemaining': time_remaining})

# Start the countdown timer
@app.route('/')
def start_timer():
    return update_timer()

if __name__ == '__main__':
    app.run()
