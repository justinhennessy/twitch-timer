#!/bin/bash

# Start the count_down.py script in the background
python count_down.py &

# Start the main Flask application
python app.py
