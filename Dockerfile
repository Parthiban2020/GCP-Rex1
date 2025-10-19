# Use the official Python image as a base
FROM python:3.11-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
COPY . .

# Ensure the .env file is NOT copied to production image
# If you were putting .env in the container, you'd add:
# COPY .env .
# But we will use Cloud Run environment variables for prod secrets

# Define the command to run your application using Gunicorn
# Cloud Run automatically sets the PORT environment variable.
CMD exec gunicorn --bind :$PORT --workers 3 --threads 8 --timeout 0 app:app