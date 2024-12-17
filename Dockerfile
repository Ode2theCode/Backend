# Use the official Python image from the Docker Hub
FROM python:3.12-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apk add --no-cache gcc musl-dev mariadb-connector-c-dev mariadb-dev pkgconfig

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --upgrade 'sentry-sdk[django]'

# Copy the project files
COPY . /app/

# Expose the port your app runs on
EXPOSE 8000

# Run the application
CMD ["daphne", "FD.asgi:application", "--bind", "0.0.0.0", "--port", "8000"]