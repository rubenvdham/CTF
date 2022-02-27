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

