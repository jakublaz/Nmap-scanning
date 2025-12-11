# Setup for Linux

## First run a few commands to prepare the system to run this container

```bash
sudo apt update
sudo apt install docker.io git make -y
sudo apt-get purge -y apparmor
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
reboot
````

## Clone this repository
### If you are running this as LXC on Proxmox :
- Make sure to enable nesting and keyctl in the privileged container options.
#### Then run on proxmox:
````bash
nano /etc/pve/lxc/container_number.conf
````
Add the following lines :
````bash
lxc.apparmor.profile: unconfined
lxc.cgroup.devices.allow: a
````
Them reboot the container.
#### Then run :

```bash
git clone https://github.com/jakublaz/Nmap-scanning.git
````

#### Now lets create a setting file for email by running this commands :
```bash
cat <<EOF > msmtprc.tpl
account default
host smtp.gmail.com
port 465
auth login
user USER@mail.com
password PASSWORD
from USER@mail.com
tls on
tls_starttls off
tls_trust_file /etc/ssl/certs/ca-certificates.crt
logfile /var/log/msmtp.log
EOF
```

### Finally give permissions to the script :
```bash
cd scripts
chmod +x run.sh
./run.sh
```

