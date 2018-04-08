import hashlib
import utils
from utils import sha256d, list_hash
import time
import json
import threading
import transaction as tr
import wallet as wa
import TxPool as pool
import p2p
# from typing import Iterable
BLOCK_GENERATION_INTERVAL = 10  # 10s
DIFFICULTY_ADJUSTMENT_INTERVAL = 3  # 10 blocks


class Block:
    def __init__(self, index, data, timestamp, hash, prev_hash, nonce, difficulty):
        self.index = index
        self.data = data  # tx[]
        self.timestamp = timestamp
        self.hash = hash
        self.prev_hash = prev_hash
        self.nonce = nonce
        self.difficulty = difficulty  # int

    #TODO data hash and tree hash
    # 计算block hash，不包括nonce
    def calculate_hash(self):
        return list_hash([str(self)])
        # return list_hash(
        #     [str(self.index), self.data, str(self.timestamp), self.prev_hash, str(self.difficulty), str(self.nonce)])

    def __eq__(self, other):
        return (
                self.index == other.index
                and self.data == other.data
                and self.timestamp == other.timestamp
                and self.hash == other.hash
                and self.prev_hash == other.prev_hash
                and self.difficulty == other.difficulty
                and self.nonce == other.nonce
        )

    def __str__(self):
        return f'Block:{self.index}\nData:{self.data}\nTime:{self.timestamp}' \
               f'\nPrevHash:{self.prev_hash}\nNonce:{self.nonce}\nDifficulty:{self.difficulty}\n'

genesisTransaction=tr.Transaction('95db0b8e71740baf81a619bfff7afe3600181828b59815d02c7f1b7b3209c831',
                                  [tr.TxIn('',0,'')],
                                  [tr.TxOut('60ba02269f0aa21a5ee18de8f21f4c159587713db66459d8baca5406021cc51269fe4b4d23587bf58c70e7014d727d1e10ec6b80fa395829b3b79dae3fdc7360',50)])

genesis_block = Block(
    index=0,
    data=[genesisTransaction],
    timestamp=1519415703,
    hash='e9d3061d5e216863506649096aac5ddd2089357c0bb3d647db332cd9b926f8b9',
    prev_hash='',
    nonce=0,
    difficulty=0  # 20 is about 5s
)

# print(genesis_block.calculate_hash())

blockchain = [genesis_block]
# utxos = []  # list of utxo
utxos = tr.processTx(blockchain[0].data,[],0)


def getBlockchain():
    return blockchain

def setBlockchain(newchain):
    global blockchain
    blockchain = newchain

def getUtxos():
    return utxos

def setUtxos(newutxos):
    global utxos
    utxos = newutxos


# return utxo.deepcopy() #why?


# ====================functions==================

def getLastBlock():
    return blockchain[-1]


# def generateEmptyNextBlock():
#     pass


# return a block with no data


def getDifficulty():
    lastBlock = getLastBlock()
    if lastBlock.index % DIFFICULTY_ADJUSTMENT_INTERVAL == 0 and lastBlock.index != 0:  # adjust
        preAdjBlock = blockchain[len(blockchain) - 1 - DIFFICULTY_ADJUSTMENT_INTERVAL]
        timeExpected = BLOCK_GENERATION_INTERVAL * DIFFICULTY_ADJUSTMENT_INTERVAL
        timeTaken = lastBlock.timestamp - preAdjBlock.timestamp
        if timeTaken < timeExpected / 2:  # too fast
            return preAdjBlock.difficulty + 1
        elif timeTaken > timeExpected * 2:  # too slow
            return preAdjBlock.difficulty - 1
        else:
            return preAdjBlock.difficulty
    else:  # keep old difficulty
        return lastBlock.difficulty


def matchDifficuilty(h, difficulty) -> bool:
    upperbound = (1 << (256 - difficulty))
    h = int(h, 16)  # convert hex to int
    if h < upperbound:
        return True
    else:
        return False


mine_interrupt = threading.Event()


# TODO: add timer and print hash rate
def mineBlock(block):
    block.nonce = 0
    mine_interrupt.clear()
    while True:
        h = block.calculate_hash()
        if block.nonce % 10000 == 0 and mine_interrupt.is_set():  # check per 1000 iters
            mine_interrupt.clear()
            return None  # stop mining
        if matchDifficuilty(h, block.difficulty):
            # return new block with nonce
            block.hash = h
            return block
        block.nonce += 1


def generateBlock_with_data(data):
    prev_block = blockchain[-1]
    difficulty = getDifficulty()
    newIndex = prev_block.index + 1
    newTime = int(time.time())  # sec
    newBlock_raw = Block(newIndex, data, newTime, '', prev_block.hash, 0, difficulty)
    newBlock = mineBlock(newBlock_raw)  # start mine block
    return newBlock #return none if interrupted


# print(generateBlock_with_data("hello"))

def assmbleDataToMineBlock():
    # choose tx data from pool block = select_from_mempool(block)
    # add coinbase and fee fees = calculate_fees(block)
    # coinbase_txn = Transaction.create_coinbase(...)
    # build a tree
    # build the block
    # call generateBlock_with_data
    coinbaseTx = tr.getCoinbaseTx(wa.getPubKeyFromWallet(),getLastBlock().index+1)
    blockData = [coinbaseTx]+pool.getTxPool() #get all tx in pool #TODO select some of txs instead of all
    return generateBlock_with_data(blockData)


#mine forever
def miner():
    while True:
        # data = "hello"
        # generateBlock_with_data(data)
        block = assmbleDataToMineBlock()
        if block:
            addBlockToChain(block)       #attach block to chain
            print(block)
            p2p.broadcast(block,"/block") #TODO:is this the same p2p? peers?
            #TODO save to disk
        #if block is empty means it was interuptted, start new loop on new block


# =========validate block========
# block类型检查
def validate_block_types(block):
    """Returns whether all of the types in the given block are correct"""
    # util.util.raisenotdefined()
    return (
            type(block.index) == int
            and type(block.data) == str
            and type(block.timestamp) == int
            and type(block.hash) == str
            and type(block.prev_hash) == str
            and type(block.nonce) == int
            and type(block.nonce) == int
    )


# print(validate_block_types(genesis_block))


def validate_genesis_block(block):
    if not genesis_block == block:
        print('Invalid genesis block')
        return False
    return True


# print(validate_genesis_block(genesis_block))

def validate_block(block, prev_block):
    """Validates a given non-genesis block, raising a ValueError if a problem
    is found"""
    if not validate_block_types(block):
        return False
        # raise ValueError('Block types invalid')
    elif block.index != prev_block.index + 1:
        return False
        # raise ValueError('Invalid block index')
    elif block.prev_hash != prev_block.hash:
        return False
        # raise ValueError('Invalid previous hash')
    elif block.calculate_hash() != block.hash:
        return False
        # raise ValueError('Invalid hash')
    #TODO check timestamp


# valide a whole chain, return utxo if ture, return None if flase
def validate_blockchain(chain):
    """When given a blockchain, validates that all blocks are valid, raising
    a ValueError if an inconsistency or other problem is found"""
    if len(chain) < 1:
        # raise ValueError('Zero-length blockchain')
        return False
    if not validate_genesis_block(chain[0]):
        return False

    res_utxos=[]
    for i in range(0, len(chain)):
        if i!=0 and (not validate_block(chain[i], chain[i - 1])):
            return None
        block:Block = chain[-1]
        res_utxos = tr.processTx(block.data,res_utxos,block.index)
        if not res_utxos:
            print("transactions is invalid")
            return None
    return res_utxos



# print(validate_blockchain([]))


def getAccumulatedDifficulty(chain):
    return sum([2 ** block.difficulty for block in chain])


#挖到新块，或者收到新块，要加到chain上
def addBlockToChain(block):
    if validate_block(block, getLastBlock()):
        res_utxos = tr.processTx(block.data,getUtxos(),block.index)
        if res_utxos:
            blockchain.append(block)
            mine_interrupt.set()#stop mining and mine on new block
            setUtxos(res_utxos) #update utxos
            pool.updateTxPool(res_utxos) #update pool
            print("The block has been accepted")
        else:
            print("the block has invalid tx")
            return False


# replace the chian with new chain if it's has more work
def replaceChain(newchain)->bool:
    res_utxos = validate_blockchain(newchain)
    if res_utxos:
        if getAccumulatedDifficulty(getBlockchain()) > getAccumulatedDifficulty(newchain):
            setBlockchain(newchain)
        setUtxos(res_utxos)
        pool.updateTxPool(res_utxos)
        # broadcast latest in p2p
        return True
    else:
        print("Received blockchain is invalid.")
        return False

# def isValidTimestamp():
# 	pass


# def addBlockToChain():
# 	pass
if __name__ == '__main__':
    # miner()
    print(getUtxos())
