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


NEED TO CREATE A PASSWORD CONST FOR SMTP - write about it
NEED TO ADD DATA VOLUME FOR CONTAINER STORAGE TO GET DIFF




wyrzucienie dodawania DNS - juz nie powinno być potrzebne

change scheduler script to enable use to write different than auto and custom targets

#### LATER:
- przygotowanie x containerów i uzywanie wolnego, albo trzworzenie nowego gdy wszystie stworzone są zajęte a potrzebna nowego

- może zapisywać wyniki do bazy danych albo pliku z bazą danych? -> wtedy można porównać wyniki czy coś się zmieniło łatwiej