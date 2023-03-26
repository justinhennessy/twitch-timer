from flask import Flask, render_template, request

app = Flask(__name__)
remaining_time = 300  # 5 minutes in seconds

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/timer')
def timer():
    return render_template('timer.html', remaining_time=remaining_time)

@app.route('/add_time')
def add_time():
    global remaining_time
    remaining_time += 30  # Add 30 seconds to the remaining time
    if remaining_time > 600:  # Limit the timer to 10 minutes
        remaining_time = 600
    return render_template('timer.html', remaining_time=remaining_time)

@app.route('/nightbot', methods=['POST'])
def nightbot():
    global remaining_time
    if request.form.get('command') == '!encore':
        remaining_time += 30  # Add 30 seconds to the remaining time
        if remaining_time > 600:  # Limit the timer to 10 minutes
            remaining_time = 600
    return 'OK'

if __name__ == '__main__':
    app.run(debug=True)

