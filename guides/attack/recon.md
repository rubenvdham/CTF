# Recon

## Scanning

### NMAP TCP quick 
````
sudo nmap -Pn -v -sS -sV -sC -oN tcp-quick.nmap {IP}
````
### NMAP TCP Full 
````
sudo nmap -Pn -sS --stats-every 3m --max-retries 1 --max-scan-delay 20 --defeat-rst-ratelimit -T4 -p1-65535 -oN tcp-full.nmap -sV {IP} 
````
### NMAP TCP - Repeat if extra ports found 
````
sudo nmap -Pn -v -sS -A -oN tcp-extra.nmap -p {PORTS} {IP} 
````
### NMAP UDP quick 
````
sudo nmap -Pn -v -sU -sV --top-ports=30 -oN udp-quick.nmap {IP}
````
### NMAP UDP top 1000 ports 
````
sudo nmap -Pn --top-ports 1000 -sU --stats-every 3m --max-retries 1 -T4 -oN udp-1000.nmap {IP}
````

### NMAP UDP - Repeat if extra ports found 
````
sudo nmap -Pn -sU -A -oN udp-extra.nmap -p {PORTS} {IP} 
````

## Enumeration

### Enum4linux

```
enum4linux {ip}
```



