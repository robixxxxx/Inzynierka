# Use a base image with Python and necessary dependencies
FROM python:3.9-slim

# Install necessary packages
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    libi2c-dev \
    i2c-tools \
    libatlas-base-dev \
    libjpeg-dev \
    libtiff5-dev \
    libjasper-dev \
    libpng-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    pigpio \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application code
COPY . /app
WORKDIR /app

# Install MediaMTX
RUN curl -L https://github.com/aler9/mediamtx/releases/download/v0.0.0/mediamtx_linux_amd64.tar.gz | tar xz -C /usr/local/bin

# Expose necessary ports
EXPOSE 12345 12346 50000 8554

# Start the application
CMD ["python", "server.py"]
