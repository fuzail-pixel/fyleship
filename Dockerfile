# Use an official Python image as a base
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy only requirements first (for better caching)
COPY requirements.txt requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Ensure SQLite is installed
RUN apt-get update && apt-get install -y sqlite3 && rm -rf /var/lib/apt/lists/*

# Expose the application port
EXPOSE 8000

# Start the application using Gunicorn
CMD ["gunicorn", "-c", "gunicorn_config.py", "core.server:app"]

