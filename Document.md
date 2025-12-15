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

OSTATNI MAIL - zmienić jak pokauzje slanowanie port i service gdy nie znajdzie
NALEży ozaczyć jakoś że coś pochodzi że schedule scan może [SCHEDULE]
ZMIANA TEMP FILE NA TEN ZAPISANY jako dorzucany do maila
przygotowanie x containerów i uzywanie wolnego, albo trzworzenie nowego gdy wszystie stworzone są zajęte a potrzebna nowego
OCZYSZCZANIE STARYCH PLIKÓW - dodać opcję clean, będzie chodziła co jakiś czas
cos jest nie tak z tworzeniem automatycznym containerów na mikrotik