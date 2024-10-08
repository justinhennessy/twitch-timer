#!/bin/bash

# Start the count_down.py script in the background with nohup
echo "Starting count_down.py..."
nohup python count_down.py > count_down.log 2>&1 &

# Give it a moment to start
sleep 2

# Check if count_down.py is running
if pgrep -f "python count_down.py" > /dev/null
then
    echo "count_down.py is running."
else
    echo "Error: count_down.py failed to start. Check count_down.log for details."
fi

# Start the main Flask application in the background
echo "Starting app.py..."
nohup python app.py > app.log 2>&1 &

# Give it a moment to start
sleep 2

# Check if app.py is running
if pgrep -f "python app.py" > /dev/null
then
    echo "app.py is running."
else
    echo "Error: app.py failed to start. Check app.log for details."
fi

# Configure ngrok with the authtoken from .env file
echo "Configuring ngrok..."
source .env
ngrok config add-authtoken $NGROK_AUTHTOKEN

# Start ngrok in the foreground
echo "Starting ngrok..."
NGROK_WEB_ADDR=0.0.0.0:4040 ngrok http --domain=www.streamtimers.com --log=stdout --log-format=json --log-level=debug 5001
