# Documentation
## How do you run this container?

### DEBUG mode :

Makes container sleep for 1 hour after execution to allow debugging.

### First target
We need to select from :
- auto
- ping 
- custom (if this give IP address after it)
### Scanning options:
#### Presets:
- fast
- normal
- deep
- vuln

####




it works now for :
- auto
- debug
- custom 192.168.0.254 --presets fast
- ping --preset fast
- ping on wrong network
- custom 192.168.0.1 -p 80,443 --script http-title
- router-arp alone for now tested



WRITE ABOUT FILES IN GIT IGNORE