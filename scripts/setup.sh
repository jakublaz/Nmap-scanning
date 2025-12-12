#!/bin/bash

# Stop the script if any command fails
set -e

echo "--- Starting System Update and Installation ---"
sudo apt update
sudo apt install docker.io git make -y

# Purge AppArmor (Scanning tools often conflict with it)
sudo apt-get purge -y apparmor

echo "--- Configuring Docker ---"
sudo systemctl enable --now docker

# Add the current user (or the user who invoked sudo) to the docker group
REAL_USER=${SUDO_USER:-$USER}
sudo usermod -aG docker "$REAL_USER"
echo "User $REAL_USER added to docker group."

echo "--- Cloning Repository ---"
# Check if directory already exists to avoid errors
if [ -d "Nmap-scanning" ]; then
    echo "Directory 'Nmap-scanning' already exists. Skipping clone."
else
    git clone https://github.com/jakublaz/Nmap-scanning.git
fi

cd Nmap-scanning

# .env Configuration ---
echo "--- Environment Configuration (.env) ---"
echo "Please configure the scanning variables."
read -p "Enter Router IP (e.g., 192.168.0.1): " ROUTER_IP
read -p "Enter Router User: " ROUTER_USER
read -sp "Enter Router Password: " ROUTER_PASS
echo "" # Newline for formatting
read -p "Enter Subnet to Scan (e.g., 192.168.0.0/24): " AUTO_SUBNET

# Create the .env file
cat <<EOF > .env
ROUTER_IP=$ROUTER_IP
ROUTER_USER=$ROUTER_USER
ROUTER_PASS=$ROUTER_PASS
AUTO=$AUTO_SUBNET
EOF
echo ".env file created successfully."

# Email Configuration
echo "--- MSMPT Configuration ---"
echo "Please enter the credentials for the msmtprc file."
read -p "Enter Gmail User (e.g., user@mail.com): " GMAIL_USER
read -sp "Enter Gmail Password: " GMAIL_PASS
echo "" # New line for formatting

# Create the config file using the variables provided
cat <<EOF > msmtprc.tpl
account default
host smtp.gmail.com
port 465
auth login
user $GMAIL_USER
password $GMAIL_PASS
from $GMAIL_USER
tls on
tls_starttls off
tls_trust_file /etc/ssl/certs/ca-certificates.crt
logfile /var/log/msmtp.log
EOF

# Add access to the whole folder
chmod -R +x Nmap-scanning/

echo "--- Setup Complete ---"
read -p "A reboot is recommended to finalize permissions. Reboot now? (y/n) " yn
case $yn in 
    [Yy]* ) sudo reboot;;
    [Nn]* ) echo "Please reboot manually later to finalize Docker group changes.";;
    * ) echo "Invalid response. Please reboot manually.";;
esac