# Setup for Linux

## First run a few commands to prepare the system to run this container

```bash
sudo apt update
sudo apt install docker.io git -y
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
````
Now logout and login again to apply usermod changes.

## Clone this repository

```bash
git clone https://github.com/jakublaz/Nmap-scanning.git