"""
Usage:
client.py show <num> [-a]
client.py send <index> <amount> <addr>

"""

from docopt import docopt
import requests
import pickle
import threading
import json

balance = {}
addr = {}


def show(num, all):
    threads = []

    for i in range(num):
        url = "http://localhost:" + str(8000 + i) + "/balance"
        threads.append(threading.Thread(target=getBalanceRequest, args=(url, i)))
        threads[-1].start()
    [t.join() for t in threads]
    # print(balance,addr)
    print('========balance==========')
    for i in range(num):
        print(i, balance[i], addr[i] if all else '')

    print("total:",sum([balance[i] for i in balance if balance[i]!=None]))
    print('=========================')


def send(index,amount,addr):
    url = "http://localhost:" + str(8000 + index) + "/send"
    params = {'amount':amount,'receiver':addr}
    try:
        r = requests.get(url,params=params)
        print("ok")
    except Exception as e:
        print(e)




def getBalanceRequest(url, index):
    global balance
    try:
        r = requests.get(url)
        res = json.loads(r.content)
        addr[index] = res['addr']
        balance[index] = res['balance']
    except Exception as e:
        print(e)
        addr[index],balance[index]=None,None
    return



if __name__ == '__main__':
    args = docopt(__doc__, argv=None, help=True, version=None, options_first=False)
    if args["show"]:
        num = int(args["<num>"])
        show(num, args['-a'])
    elif args["send"]:
        index = int(args['<index>'])
        amount= int(args['<amount>'])
        addr = args['<addr>']
        send(index,amount,addr)
