"""
Usage: p2p.py <port>
"""
from flask import Flask, jsonify,request
import pickle
import requests
import chain
import json
import threading
# from chain import Block
import TxPool as pool
import transaction as tr
from docopt import docopt
import  utils
import os


app = Flask(__name__)

# selfip = ""
# peers=[] #read from file list of ip

tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol', 
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web', 
        'done': False
    }
]

# #TODO read url filter url ,build peer list
# def readUrlfromFile():
#     #fill peerip TODO read ip from file
#     global peers
#     li = ["http://localhost:8001","http://localhost:8002"]
#     li.remove(selfip)#remove selfip
#     peers = li
#     return

def broadcast(data, route):
    #send to all peer
    print("broadcast:",utils.peers)
    for url in utils.peers:
        postRequest(url+route,data)


@app.route('/querylast', methods=['GET'])
def querylast():
    #return last block
    return pickle.dumps(chain.getLastBlock())

@app.route('/queryall', methods=['GET'])
def queryall():
    return pickle.dumps(chain.blockchain)

# @app.route('/querytx', methods=['GET'])
# def querytx():
#     #return the pool
#     return pickle.dumps

# @app.route('/chain', methods=['POST'])
# def receiveChain():
#     content = request.data
#     print(content)
#     obj = json.dumps(content)
#     return "ok"

@app.route('/block', methods=['POST'])
def receiveBlock():
    content = request.data
    print(content)
    obj = pickle.dumps(content)
    receiveBlockHandler(obj)
    return "ok"

@app.route('/tx', methods=['POST'])
def receiveTx():
    content = request.data
    print(content)
    obj = pickle.dumps(content)
    receiveTxhandler(obj)
    return "ok"

# r = requests.post("http://bugs.python.org", data={'number': 12524, 'type': 'issue', 'action': 'show'})

def getRequest(url) -> dict:
    r = requests.get(url)
    print(r.content)
    return pickle.loads(r.content)

def postRequest(url, data):
    try:
        r = requests.post(url, data)
        return pickle.loads(r.content)
    except:
        print("connection error")
        return None

#TODO when edit chain , add lock
#when receive a block
def receiveBlockHandler(block):
    if not chain.validate_block_types(block):
        print("block structuture not valid")
        return
    lastblock = chain.getLastBlock()
    #if block exist, then index must be smaller, so don't broadcast and do nothing
    if block.index > lastblock.index: #only when receive longer chain's block
        if lastblock.hash ==  block.prev_hash: # one block behind
            chain.addBlockToChain(block)
            broadcast(block,"/block")
        else: #serveral blocks behind, or branch
            addr = request.remote_addr
            #broadcast request query all chain
            getAndReplaceChain(addr)




def getAndReplaceChain(addr):
    otherchain = getRequest(addr+"/queryall")
    if chain.replaceChain(otherchain):
        broadcast(otherchain[-1], "/block") #broadcast block


#when receive tx
def receiveTxhandler(tx):
    if pool.addToTxPool(tx,chain.getUtxos()):#add tx to pool
        broadcast(tx,"/tx")#broadcast
    #if tx exist, don't broadcast


def http_server(port):
    app.run(debug=False, host='0.0.0.0', port=port)

def main(port):
    utils.readUrlfromFile()
    print("peers:", utils.peers)
    threads = []
    def start_thread(fnc): #启动线程的函数
        threads.append(threading.Thread(target=fnc, daemon=True))
        threads[-1].start()

    print("start utxos:",chain.getUtxos())
    start_thread(chain.miner)
    start_thread(http_server(port))
    [t.join() for t in threads]#main thread join to wait two subthread


if __name__ == '__main__':
    args = docopt(__doc__, argv=None, help=True, version=None, options_first=False)
    port = int(args["<port>"])
    # print(port)
    utils.selfip = f"http://localhost:{port}"
    print("start main")
    main(port)
    # http_server(port)

