# Linux - Upgrading Reverse Shells

## victim

```
reset
python -c 'import pty;pty.spawn("/bin/bash")';
export SHELL="bash";export TERM="xterm";stty rows 38 columns 116;
```

## host

Ctrl+Z

```
stty raw -echo
fg
```