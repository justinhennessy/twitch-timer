import time

file_path = 'timer.txt'

def countdown_timer():
    while True:
        with open(file_path, 'r') as file:
            time_value = float(file.read())

        # Pause countdown if timer is -1 or -999
        if time_value not in [-1, -999]:
            time_value = max(time_value - 1, 0)  # Reduce the timer by 1 second, minimum is 0

            with open(file_path, 'w') as file:
                file.write(str(time_value))

        time.sleep(1)  # Sleep for 1 second, regardless of timer value

if __name__ == "__main__":
    countdown_timer()
