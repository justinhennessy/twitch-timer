#!/bin/bash

# Run the Python backend with STDOUT redirected to backend.log
python backend.py > backend.log 2>&1 &

# Run ngrok and redirect its STDOUT to ngrok.log
ngrok http 5000 > ngrok.log 2>&1 &

# Run the Python HTTP server with STDOUT redirected to server.log
python -m http.server 8000 > server.log 2>&1 &

# Provide feedback that processes are started
echo "Processes started in the background. You can access their logs in respective log files."

