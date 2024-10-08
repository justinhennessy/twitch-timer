# Use Python 3.11 as the base image
FROM python:3.11-slim

# Set working directory in the container
WORKDIR /app

# Install necessary packages and create ngrok config
RUN apt-get update && apt-get install -y procps wget gnupg2 curl && \
    curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | gpg --dearmor -o /usr/share/keyrings/ngrok-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/ngrok-archive-keyring.gpg] https://ngrok-agent.s3.amazonaws.com buster main" | tee /etc/apt/sources.list.d/ngrok.list && \
    apt-get update && \
    apt-get install -y ngrok && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /root/.config/ngrok && \
    echo "web_addr: 0.0.0.0:4040" >> /root/.config/ngrok/ngrok.yml


# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Make the start script executable
RUN chmod +x start.sh

# Expose the ports the app runs on
EXPOSE 5001 4040

# Command to run the start script
CMD ["./start.sh"]
