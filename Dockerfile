# Use a specific version tag for the Selenium standalone image
FROM selenium/standalone-chromium:latest

# Set the working directory
WORKDIR /app

# Install pip and necessary dependencies
USER root
RUN apt-get update && apt-get install -y python3 wget python3-venv

# Set up a virtual environment
RUN python3 -m venv venv

# Activate the virtual environment and install pip and selenium
RUN /app/venv/bin/pip install --upgrade pip
RUN /app/venv/bin/pip install selenium

# Copy the requirements.txt and install dependencies in the virtual environment
COPY requirements.txt .
RUN /app/venv/bin/pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Specify the entry point for the application using the virtual environment's Python
ENTRYPOINT ["/app/venv/bin/python", "main.py"]