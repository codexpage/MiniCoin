this file is intended to explain how to run MiniCoin

to start a node:
in utils.py about line65-70, something like:
        for p in range (8001, 8010):
            li.append(base + ":" + str(p))
the numbers refer to port number that could(would) http listener binds
so simple run "python3 p2p.py 8001"
a node binds port 8001 started

to test concurrency:
simple run "./start <num>"
num could be any positive integer
to start that many nodes at the same time
default start port is 8000, increase by 1 refers to <num>

to kill node thread:
run "./kill <num>"

to test nodes by step
run "./advTest"
but parameters in advTest need to be modified mannually

to get overview of balance and test transactions
overview of balance: run "python3 client.py show <num> -a"
transactions: run "python3 client.py send <index> <amount> <addr>"
addr refers to address shown by overview

output directories:
blockchain to chains with port number as suffix
private keys to key with port number as suffix
log to testres with with port number as suffix
node that ever contacted to to peerlist with port number as suffix

note: only run ./start could log output to right directory

right way to kill a thread
kill -2 <pid>

./detectport if needed:
find out pid that bind some port
