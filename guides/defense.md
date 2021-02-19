# Defense Strategies & Tools

## Intrusion detection

- Check for **logs**:
  - Apache: /var/log/apache2/access.log


- Check for active **users**:
`w`
- Check for installed SSH **authorized_keys**

### Detecting shells
1. Look for (reverse) shells in the process tree:
`ps -eaf --forest`

2. Grab current working directory:
`ls -al /proc/pid | grep cwd`
3. Grab network socket stats for pid:
`ss -anp pid | grep pid`




## Networking

- grab all network stats:
`ss -lnpt`
- capture network traffic
`tcpdump -i interface -w output.pcap -n 'not port 22' -s 0`

