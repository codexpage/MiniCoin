"""
Usage: p2p.py <port>
"""
from flask import Flask, jsonify,request
import pickle
import requests
import chain
import json
import threading
import TxPool as pool
from docopt import docopt
import  wallet as w
import  utils
import datetime
import time
import signal
import random
app = Flask(__name__)
requests.adapters.DEFAULT_RETRIES = 0
lock = threading.Lock()
serverStart = False


def broadcast(data, route):
    #send to all peer
    print("broadcast:",len(utils.live), utils.live)

    threads = []
    for url in utils.live:
        t = threading.Thread(target=postRequest, args=(url+route,data))
        threads.append(t)
        t.start()


@app.route('/querylast', methods=['GET'])
def querylast():
    return pickle.dumps(chain.getLastBlock())

@app.route('/queryall', methods=['GET'])
def queryall():
    print("send all chain")
    return pickle.dumps(chain.blockchain)


@app.route('/block', methods=['POST'])
def receiveBlock():
    content = request.get_data()
    obj = pickle.loads(content)
    receiveBlockHandler(obj)
    return "ok"

@app.route('/tx', methods=['POST'])
def receiveTx():
    content = request.get_data()
    obj = pickle.loads(content)
    receiveTxhandler(obj)
    return "ok"


@app.route('/balance', methods=['GET'])
def getBalance():
    addr = w.getPubKeyFromWallet()
    return json.dumps({'addr':addr,'balance':w.getBalance(addr,chain.getUtxos())})

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
    peer = pickle.loads(content)
    addtoLive(str(peer))
    syncPeer(str(peer))
    return "live"


def syncPeer(peer):
    if peer not in utils.everContact:
        utils.everContact.append(peer)

        # simulate a partially connectect network
        # random.shuffle(utils.everContact)
        # part = utils.everContact[:len(utils.everContact)//4]
        # utils.live = part
        utils.live = utils.everContact

def getHeartBeat():
    while True:

        for p in utils.everContact:
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
    return pickle.loads(r.content)

def postRequest(url, data):
    try:
        r = requests.post(url, pickle.dumps(data))
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
        for p in utils.live:
            if getAndReplaceChain(p):
                break;
        # pass


#when receive tx
def receiveTxhandler(tx):
    if tx is not None:
        if pool.addToTxPool(tx,chain.getUtxos()):#add tx to pool
            broadcast(tx,"/tx")#broadcast
        else:
            print("receive a invalid tx")
    else:
        print("void tx")
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
    http_server(port)
    [t.join() for t in threads]#main thread join to wait two subthread


if __name__ == '__main__':
    args = docopt(__doc__, argv=None, help=True, version=None, options_first=False)
    port = int(args["<port>"])
    utils.selfip = f"http://localhost:{port}"
    utils.peerList += str(port)
    w.privateKeyPath += str(port)
    chain.storage += str(port)
    print("start main")
    signal.signal(signal.SIGINT, chain.flush)

    main(port)

