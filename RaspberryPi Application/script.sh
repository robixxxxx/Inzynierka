#!/bin/bash

# Check if the script is run with sudo
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (use sudo)"
  exit 1
fi
systemctl daemon-reload
#Enable i2c bus
raspi-config nonint do_i2c 0
# Enable camera
raspi-config nonint do_camera 0

# Get the directory of the script
SCRIPT_DIR=$(dirname "$(realpath "$0")")
echo "Script directory: $SCRIPT_DIR"
# Disable Overlay File System
echo "Disabling Overlay File System..."
raspi-config nonint disable_overlayfs

echo "Updating package lists..."
apt-get update

echo "Installing required packages..."
apt-get install -y \
    hostapd dnsmasq network-manager iw \
    libi2c-dev i2c-tools \
    python3-rpi.gpio \
    gcc g++ make cmake \
    libcap-dev \
    libopencv-dev python3-opencv \
    libavcodec-dev libavformat-dev libavdevice-dev libavutil-dev libavfilter-dev libswscale-dev libswresample-dev \
    pkg-config libjpeg-dev zlib1g-dev \
    python3-venv \
    ffmpeg \
    libavcodec-extra \
    git

echo "Cleaning up..."
apt-get clean
rm -rf /var/lib/apt/lists/*

# Install Python dependencies
sudo apt install python3 -y
wget https://bootstrap.pypa.io/get-pip.py
sudo python3 get-pip.py

# Check if requirements.txt exists
if [ ! -f "$SCRIPT_DIR/requirements.txt" ]; then
  echo "Error: requirements.txt not found in $SCRIPT_DIR."
  exit 1
fi

echo "Installing Python dependencies from requirements.txt..."
python3 -m pip install --break-system-packages --no-cache-dir -r "$SCRIPT_DIR/requirements.txt"


echo "Python dependencies installed successfully."

# Set device name, this will be used to identify the device
echo "Set device name"
read device_name

# Validate the hostname
if [[ ! "$device_name" =~ ^[a-zA-Z0-9-]+$ || "$device_name" =~ ^- || "$device_name" =~ -$ ]]; then
  echo "Invalid hostname. It must consist of letters, numbers, and hyphens, and cannot start or end with a hyphen."
  exit 1
fi

# Ensure the file exists
SERVER_FILE="$SCRIPT_DIR/src/server/server.py"
if [ ! -f "$SERVER_FILE" ]; then
  echo "Error: File '$SERVER_FILE' not found."
  exit 1
fi
HOSTAPD_FILE="$SCRIPT_DIR/etc/hostapd/hostapd.conf"
if [ ! -f "$HOSTAPD_FILE" ]; then
  echo "Error: File '$HOSTAPD_FILE' not found."
  exit 1
fi

# Use sed to replace the value of the name element
echo "Updating device name"
sed -i 's/"name": "RaspberryPiControlServer"/"name": "'"$device_name"'"/' "$SERVER_FILE"
sed -i 's/^ssid=.*/ssid='"$device_name"'/' "$HOSTAPD_FILE"
# Copy necessary files and folders from /etc
echo "Copying necessary files and folders from /etc..."
cp -r "$SCRIPT_DIR/etc/hostapd" /etc/
cp -r "$SCRIPT_DIR/etc/dnsmasq.conf" /etc/

chmod +x "$SCRIPT_DIR/app.py"

# Create systemd service file
SERVICE_FILE="/etc/systemd/system/raspberrypi_app.service"
echo "Creating systemd service file at $SERVICE_FILE"
cat > $SERVICE_FILE <<EOL
[Unit]
Description=Raspberry Pi Application
After=network.target

[Service]
ExecStart=/usr/bin/python3 $SCRIPT_DIR/app.py
WorkingDirectory=$SCRIPT_DIR
StandardOutput=file:/var/log/raspberrypi_app.log
StandardError=file:/var/log/raspberrypi_app.log
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
EOL

# Reload systemd, enable and start the service
echo "Reloading systemd, enabling and starting the service"
systemctl daemon-reload
systemctl enable raspberrypi_app.service
systemctl start raspberrypi_app.service

# Enable Overlay File System
echo "Enabling Overlay File System..."
raspi-config nonint enable_overlayfs

echo "Setup complete. The application will start on boot."