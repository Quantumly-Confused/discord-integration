# Get a python runtime, 3.10 has what the code needs
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# add requirements file to container
COPY requirements.txt .

# Install dependencies the usual way
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app code into the container
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "main.py"]