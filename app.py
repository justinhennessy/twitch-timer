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

@app.route('/nightbot', methods=['GET', 'POST'])
def nightbot():
    global remaining_time
    if request.method == 'GET':
        command = request.args.get('command')
    elif request.method == 'POST':
        command = request.form.get('command')
    else:
        return 'Invalid request method'

    if command == '!encore':
        remaining_time += 30  # Add 30 seconds to the remaining time
        if remaining_time > 600:  # Limit the timer to 10 minutes
            remaining_time = 600
        return 'OK'
    else:
        return 'Invalid command'

if __name__ == '__main__':
    app.run(debug=True)

