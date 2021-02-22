# Linux - Upgrading Reverse Shells

## host

Ctrl+Z

```
stty raw -echo
fg
```

## victim

```
reset
export SHELL="bash";export TERM="xterm";stty rows 38 columns 116;
```