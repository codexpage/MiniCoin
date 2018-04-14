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
import  wallet as w
import  utils
import os
import datetime
import time
import signal
import random
import itertools
app = Flask(__name__)
requests.adapters.DEFAULT_RETRIES = 0
lock = threading.Lock()
serverStart = False

# requests.adapters.DEFAULT_RETRIES
# selfip = ""
# peers=[] #read from file list of ip


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
    print("broadcast:",len(utils.live), utils.live)
    # for url in utils.peers:
    #     postRequest(url+route,data)
    threads = []
    for url in utils.live:
        t = threading.Thread(target=postRequest, args=(url+route,data))
        threads.append(t)
        t.start()
# def post(dest, msg):
#     postRequest(dest ,msg)

@app.route('/querylast', methods=['GET'])
def querylast():
    #return last block
    return pickle.dumps(chain.getLastBlock())

@app.route('/queryall', methods=['GET'])
def queryall():
    print("send all chain")
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
    content = request.get_data()
    # print(content)
    obj = pickle.loads(content)
    receiveBlockHandler(obj)
    return "ok"

@app.route('/tx', methods=['POST'])
def receiveTx():
    content = request.get_data()
    # print(content)
    obj = pickle.loads(content)
    receiveTxhandler(obj)
    return "ok"


@app.route('/balance', methods=['GET'])
def getBalance():
    addr = w.getPubKeyFromWallet()
    return "Address:"+addr+"\n"+str(w.getBalance(addr,chain.getUtxos()))

#self node send money to others
@app.route('/send', methods=['GET'])
def sendMoney():
   amount = int(request.args['amount'])
   receiver = request.args['receiver']
   tx = w.createTx(receiver, amount, w.getPrivateKeyFromWallet(), chain.getUtxos(), pool.getTxPool())
   receiveTxhandler(tx) # receive from self
   return "ok"


@app.route('/heartbeat', methods=["POST"])
def heartBeat():
    content = request.get_data()
    # print(content)
    peer = pickle.loads(content)
    addtoLive(str(peer))
    syncPeer(str(peer))
    return "live"
# r = requests.post("http://bugs.python.org", data={'number': 12524, 'type': 'issue', 'action': 'show'})


def syncPeer(peer):
    if peer not in utils.everContact:
        utils.everContact.append(peer)


        # simulate a partially connectect network
        random.shuffle(utils.everContact)
        part = utils.everContact[:len(utils.everContact)//4]
        utils.live = part

def getHeartBeat():
    while True:

        for p in utils.live:
            try:
                r = requests.post(p + "/heartbeat", pickle.dumps(utils.selfip))
                print("heart beat of ", p, r.content)
                if r.content == b"live":
                    continue
                else:
                    updateConnection(p)
            except:
                updateConnection(p)
        time.sleep(10)

def updateConnection(peer):
    if peer in utils.live:
        utils.live.remove(peer)

def addtoLive(peer):
    if peer in utils.peers and peer not in utils.live:
        utils.live.append(peer)

def getRequest(url) -> dict:
    r = requests.get(url)
    # print(r.content)
    return pickle.loads(r.content)

def postRequest(url, data):
    try:
        r = requests.post(url, pickle.dumps(data))
        # print(r.content)
        return pickle.loads(r.content)
    except Exception as e:
        print(e)
        return None

#TODO when edit chain , add lock
#when receive a block
def receiveBlockHandler(blockandip):
    block,ip = blockandip
    print("from",ip,"======A block received=========,{time: %H:%M:%S}".format(time =datetime.datetime.now())," current length", len(chain.blockchain))
    print(block.index)
    print("=============================")
    if not chain.validate_block_types(block):
        print("block structuture not valid")
        return
    lastblock = chain.getLastBlock()
    #if block exist, then index must be smaller, so don't broadcast and do nothing
    if block.index > lastblock.index: #only when receive longer chain's block
        if lastblock.hash ==  block.prev_hash: # one block behind
            print("one block behind, add to chain")
            if chain.addBlockToChain(block):
                chain.mine_interrupt.set()  # stop mining and mine on new block
                broadcast((block,utils.selfip),"/block") #and broad cast received block
        else: #serveral blocks behind, or branch
            # addr = request.remote_addr

            #broadcast request query all chain
            print("need to replace chain from",ip)
            th=threading.Thread(target=getAndReplaceChain,args=(ip,), daemon=True)
            th.start()
    else:
        print("this block is from a shorter chain")




def getAndReplaceChain(ip):
    print("request a chain")
    try:
        otherchain = getRequest(ip+"/queryall")
    except Exception as e:
        print(str(e))
        return False

    if otherchain:
        print("longer chain getted")
        with lock:
            if chain.replaceChain(otherchain):
                broadcast((otherchain[-1],utils.selfip), "/block") #broadcast block
                print("replaced chain")
                return True
    else:
        return False


def initProgress():
        # for p in utils.live:
        #     if getAndReplaceChain(p):
        #         break;
        pass


#when receive tx
def receiveTxhandler(tx):
    if pool.addToTxPool(tx,chain.getUtxos()):#add tx to pool
        broadcast(tx,"/tx")#broadcast
    else:
        print("receive a invalid tx")
    #if tx exist, don't broadcast


def http_server(port):
    app.run(debug=False, host='0.0.0.0', port=port)

def main(port):
    utils.readUrlfromFile()
    w.initWallet()
    print("peers:", utils.live)
    threads = []
    def start_thread(fnc): #启动线程的函数
        threads.append(threading.Thread(target=fnc, daemon=True))
        threads[-1].start()

    print("start utxos:",chain.getUtxos())
    start_thread(chain.miner)
    start_thread(getHeartBeat)
    # start_thread(http_server(port))
    http_server(port)
    [t.join() for t in threads]#main thread join to wait two subthread


if __name__ == '__main__':
    args = docopt(__doc__, argv=None, help=True, version=None, options_first=False)
    port = int(args["<port>"])
    # print(port)
    utils.selfip = f"http://localhost:{port}"
    utils.peerList += str(port)
    w.privateKeyPath += str(port)
    chain.storage += str(port)
    print("start main")
    signal.signal(signal.SIGINT, chain.flush)

    main(port)
    # http_server(port)

