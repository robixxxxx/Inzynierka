#!/bin/bash

# Check if the script is run with sudo
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (use sudo)"
  exit 1
fi

#Enable i2c bus
raspi-config nonint do_i2c 0
# Enable camera
raspi-config nonint do_camera 0

echo "Updating package lists..."
apt-get update
apt-get update --fix-missing

sudo apt install -y \
      python3-distutils \
      python3-pip \
      hostapd \
      dnsmasq \
      iw \
      network-manager \
      pigpiod \
      libcap-dev \
      libopencv-dev python3-opencv \
      libavcodec-dev libavformat-dev libavdevice-dev libavutil-dev libavfilter-dev libswscale-dev libswresample-dev \
      pkg-config libjpeg-dev zlib1g-dev \

sudo pip install flask
sudo pip install smbus2
sudo pip install pigpio
sudo pip install picamera2



echo "Set device name"
read device_name

SCRIPT_DIR=$(dirname "$(realpath "$0")")
echo "Script directory: $SCRIPT_DIR"
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

if [[ ! "$device_name" =~ ^[a-zA-Z0-9-]+$ || "$device_name" =~ ^- || "$device_name" =~ -$ ]]; then
  echo "Invalid hostname. It must consist of letters, numbers, and hyphens, and cannot start or end with a hyphen."
  exit 1
fi

sed -i 's/"name": "RaspberryPiControlServer"/"name": "'"$device_name"'"/' "$SERVER_FILE"
sed -i 's/^ssid=RaspberryPiAP/ssid='"$device_name"'/' "$HOSTAPD_FILE"

chmod +x "$SCRIPT_DIR/app.py"

SERVICE_FILE="/etc/systemd/system/raspberrypi_app.service"
echo "Creating systemd service file at $SERVICE_FILE"
cat > $SERVICE_FILE <<EOL
[Unit]
Description=Raspberry Pi Application
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=sudo python3 $SCRIPT_DIR/app.py
WorkingDirectory=$SCRIPT_DIR
StandardOutput=file:/var/log/raspberrypi_app.log
StandardError=file:/var/log/raspberrypi_app.log
Restart=always
RestartSec=5
User=pi

[Install]
WantedBy=multi-user.target
EOL

echo "Copying necessary files and folders from /etc..."
sudo cp -r "$SCRIPT_DIR/etc/hostapd" /etc/
sudo cp -r "$SCRIPT_DIR/etc/dnsmasq.conf" /etc/

echo "Reloading systemd, enabling and starting the service"
systemctl daemon-reload
systemctl enable raspberrypi_app.service
systemctl start raspberrypi_app.service

systemctl enable pigpiod
systemctl start pigpiod

echo "Konfiguracja raspi-config dla NetworkManager..."
raspi-config nonint do_netconf 2
