# Setup for Linux

 If you are running this as LXC on Proxmox :
- Make sure to enable nesting and keyctl in the unprivileged container options.
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

## First run a command to prepare the system to run this container

Go to github.com/jlaz/Nmap-scanning and copy the setup.sh from Scripts folder to your machine.
Run the following commands in terminal :
```bash
chmod +x setup.sh
sudo ./setup.sh
```

#### Then to run the scanning just use this command:

```bash
cd Nmap-scanning/scripts
./run.sh
```