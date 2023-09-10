#!/bin/bash
# Define the names of the processes to be killed
process_names=("backend.py" "ngrok" "python -m http.server")

# Iterate through the process names and kill any matching processes
for process_name in "${process_names[@]}"; do
    pkill -f "$process_name"
done

echo "Processes have been terminated."

