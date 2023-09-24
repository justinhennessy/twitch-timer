#!/bin/bash

# List of commands to run in separate panes with custom titles
commands=(
    "echo 'Counter service is starting ...'; python count_down.py"
    "echo 'ngrok is starting ...'; ngrok http 5000"
    "echo 'Backend API starting ...'; python backend.py"
)

# List of corresponding custom titles
titles=(
    "Timer counting service"
    "ngrok service"
    "Backend API"
)

# Loop through the commands and open each in a new iTerm window
for i in "${!commands[@]}"; do
    cmd="${commands[i]}"
    title="${titles[i]}"
    
    osascript -e "tell application \"iTerm\"
        activate
        set newWindow to (create window with default profile)
        tell newWindow
            tell current session
                write text \"$cmd\"
            end tell
        end tell
    end tell"
done
