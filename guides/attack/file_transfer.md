# File Transfer

## Serve

### FTP 
````
Python –c pyftpdlib –p 21 –write
````

### HTTP 
````
sudo python3 -m http.server 80 
sudo python -m SimpleHTTPServer 80 
````

### SMB 
````
sudo impacket-smbserver <sharename> <share path>
````
