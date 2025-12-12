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

# Enter the repository
cd Nmap-scanning

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

echo "--- Executing Run Script ---"
# Check if the scripts directory exists (Fixing the 'cd scriptschmod' typo)
if [ -d "scripts" ]; then
    cd scripts
    chmod +x run.sh
    
    # Executing the script. 
    # Note: Since this setup script is running as root (sudo), 
    # ./run.sh will also run as root, avoiding docker permission issues.
    ./run.sh
else
    echo "Error: 'scripts' directory not found inside Nmap-scanning."
    exit 1
fi

echo "--- Setup Complete ---"
read -p "A reboot is recommended to finalize permissions. Reboot now? (y/n) " yn
case $yn in 
    [Yy]* ) sudo reboot;;
    [Nn]* ) echo "Please reboot manually later to finalize Docker group changes.";;
    * ) echo "Invalid response. Please reboot manually.";;
esac