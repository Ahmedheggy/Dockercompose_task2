# Use an official Python image as a base
FROM python:3.11

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install dependencies listed in requirements.txt   (RUN for running commands during image building)
RUN pip install --no-cache-dir -r requirements.txt

# Install PostgreSQL client to allow connection from the app
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

# Copy all files to container
COPY . .

# Expose the application port (flask)
EXPOSE 5000

# Run the Flask app after container is build
CMD ["python", "app.py"]
