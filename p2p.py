from flask import Flask, jsonify,request
import pickle
import requests
import chain
import json
import threading

app = Flask(__name__)

selfip = ""
peers=[] #read from file list of ip 

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

def readUrlfromFile():
    #fill peerip
    pass

def broadcast(data, route):
    #send to all peer
    for url in peers:
        postRequest(url+route,data)


@app.route('/querylast', methods=['GET'])
def querylast():
    #return last block
    return jsonify(chain.getLastBlock())

@app.route('/queryall', methods=['GET'])
def queryall():
    return jsonify(chain.blockchain)

@app.route('/querytx', methods=['GET'])
def querytx():
    #return the pool
    return jsonify()

# @app.route('/chain', methods=['POST'])
# def receiveChain():
#     content = request.getjson()
#     print(content)
#     obj = json.dumps(content)
#     return "ok"

@app.route('/block', methods=['POST'])
def receiveBlock():
    content = request.getjson()
    print(content)
    obj = json.dumps(content)
    receiveBlockHandler(obj)
    return "ok"

@app.route('/tx', methods=['POST'])
def receiveTx():
    content = request.getjson()
    print(content)
    obj = json.dumps(content)
    receiveTxhandler(obj)
    return "ok"

# r = requests.post("http://bugs.python.org", data={'number': 12524, 'type': 'issue', 'action': 'show'})

def getRequest(url) -> dict:
    r = requests.get(url)
    return r.json()

def postRequest(url, data) -> dict:
    r = requests.post(url, data)
    return r.json()


def receiveBlockHandler(block:chain.Block):
    if not chain.validate_block_types(block):
        print("block structuture not valid")
        return
    lastblock = chain.getLastBlock()
    if block.index > lastblock.index: #receive longer chain's block
        if lastblock.hash ==  block.prev_hash: # one block behind
            chain.addBlockToChain(block)
            broadcast(block,"/block")
        else: #serveral blocks behind, or branch
            addr = request.remote_addr
            #broadcast request query all chain
            getAndReplaceChain(addr)


def receiveTxhandler():
    #put into pool
    #braodcast
    pass



def getAndReplaceChain(addr):
    otherchain = getRequest(addr+"/queryall")
    if not chain.validate_blockchain(otherchain):#verify chain
        print("receive a invalid block chain")
        return
    if len(otherchain)>len(chain.blockchain): #should compare difficult
        chain.blockchain = otherchain
    broadcast(otherchain[-1], "/block")
    #broadcast block



def receiveTxhandler(tx):
    # addToTransactionPool(tx)
    pass
    #add tx to pool
    #broadcast


def http_server():
    app.run(debug=True)


def miner():
    pass

def main():
    readUrlfromFile()
    threads = []
    def start_thread(fnc): #启动线程的函数
        threads.append(threading.Thread(target=fnc, daemon=True))
        threads[-1].start()

    start_thread(http_server)
    # start_thread(miner)
    [t.join() for t in threads]


if __name__ == '__main__':
    main()
    # app.run(debug=True)
