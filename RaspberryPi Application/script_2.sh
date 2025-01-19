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

sudo apt install python3-distutils
apt install python3-pip
apt install hostapd
apt install dnsmasq
apt install iw
apt install network-manager

sudo pip install flask
sudo pip install smbus2
sudo pip install pigpio
sudo pip install picamera2

echo "Set device name"
read device_name

SCRIPT_DIR=$(dirname "$(realpath "$0")")

if [[ ! "$device_name" =~ ^[a-zA-Z0-9-]+$ || "$device_name" =~ ^- || "$device_name" =~ -$ ]]; then
  echo "Invalid hostname. It must consist of letters, numbers, and hyphens, and cannot start or end with a hyphen."
  exit 1
fi

sed -i 's/"name": "RaspberryPiControlServer"/"name": "'"$device_name"'"/' "$SERVER_FILE"
sed -i 's/^ssid=.*/ssid='"$device_name"'/' "$HOSTAPD_FILE"

chmod +x "$SCRIPT_DIR/app.py"

SERVICE_FILE="/etc/systemd/system/raspberrypi_app.service"
echo "Creating systemd service file at $SERVICE_FILE"
cat > $SERVICE_FILE <<EOL
[Unit]
Description=Raspberry Pi Application
After=network.target

[Service]
ExecStart=sudo python3 $SCRIPT_DIR/app.py
WorkingDirectory=$SCRIPT_DIR
StandardOutput=file:/var/log/raspberrypi_app.log
StandardError=file:/var/log/raspberrypi_app.log
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
EOL

echo "Copying necessary files and folders from /etc..."
cp -r "$SCRIPT_DIR/etc/hostapd" /etc/hostapd
cp -r "$SCRIPT_DIR/etc/dnsmasq.conf" /etc/

echo "Reloading systemd, enabling and starting the service"
systemctl daemon-reload
systemctl enable raspberrypi_app.service
systemctl start raspberrypi_app.service

echo "Konfiguracja raspi-config dla NetworkManager..."
raspi-config nonint do_netconf 2