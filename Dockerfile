# Use Python 3.11 as the base image
FROM python:3.11-slim

# Set working directory in the container
WORKDIR /app

# Install procps package which includes the ps command, and wget to download ngrok
RUN apt-get update && apt-get install -y procps wget && rm -rf /var/lib/apt/lists/*

# Install ngrok
RUN wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.tgz && \
    tar xvzf ngrok-stable-linux-amd64.tgz -C /usr/local/bin && \
    rm ngrok-stable-linux-amd64.tgz

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Make the start script executable
RUN chmod +x start.sh

# Expose the port the app runs on
EXPOSE 5001

# Command to run the start script
CMD ["./start.sh"]
