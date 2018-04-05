import hashlib
import utils
from utils import sha256d,list_hash
import time

BLOCK_GENERATION_INTERVAL=10 #10s
DIFFICULTY_ADJUSTMENT_INTERVAL=10 #10 blocks

class Block:
    def __init__(self, index, data, timestamp, hash, prev_hash,nonce, difficulty):
        self.index = index
        self.data = data #tx[]
        self.timestamp = timestamp
        self.hash = hash
        self.prev_hash = prev_hash
        self.nonce = nonce
        self.difficulty = difficulty #int

    #计算block hash，不包括nonce
    def calculate_hash(self):
        return list_hash([str(self.index), self.data, str(self.timestamp), self.prev_hash, str(self.difficulty), str(self.nonce)])

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
    	return f'Block:{self.index}\nData:{self.data}\nTime:{self.timestamp} \
    	\nHash:{self.hash}\nPrevHash:{self.prev_hash}\nNonce:{self.nonce}\nDifficulty:{self.difficulty}\n'


# genesisTransaction = {
#     'txIns': [{'signature': '', 'txOutId': '', 'txOutIndex': 0}],
#     'txOuts': [{
#         'address': '04bfcab8722991ae774db48f934ca79cfb7dd991229153b9f732ba5334aafcd8e7266e47076996b55a14bf9913ee3145ce0cfc1372ada8ada74bd287450313534a',
#         'amount': 50
#     }],
#     'id': 'e655f6a5f26dc9b4cac6e46f52336428287759cf81ef5ff10854f69d68f43fa3'
# }


genesis_block = Block(
    index = 0,
    data = 'Genesis Block',
    timestamp = 1519415703,
    hash = 'e9d3061d5e216863506649096aac5ddd2089357c0bb3d647db332cd9b926f8b9',
    prev_hash = '',
    nonce = 0,
    difficulty = 0 #20 is about 5s
)

# print(genesis_block.calculate_hash())

blockchain = [genesis_block]
utxos = [] #list of utxo

def getBlockchain():
	return blockchain

def getUtxos():
	return utxo.deepcopy() #why?



#====================functions==================

def getDifficulty():
	pass

def getAdjustedDifficulty():
	pass

def  generateEmptyNextBlock():
	pass
	#return a block with no data

def getMyUtxos():
	pass
	#return utxos




#Input a block with default nonce

def getDifficulty():
	lastBlock= blockchain[-1]
	if lastBlock.index % DIFFICULTY_ADJUSTMENT_INTERVAL ==0 and lastBlock.index !=0:
		preAdjBlock = blockchain[len(blockchain)-1-DIFFICULTY_ADJUSTMENT_INTERVAL]
		timeExpected = BLOCK_GENERATION_INTERVAL * DIFFICULTY_ADJUSTMENT_INTERVAL
		timeTaken = lastBlock.timestamp -preAdjBlock.timestamp
		if timeTaken < timeExpected / 2: #too fast
			return preAdjBlock.difficulty + 1
		elif timeTaken > timeExpected * 2: #too slow
			return preAdjBlock.difficulty - 1
		else:
			return preAdjBlock.difficulty
	else:
		return lastBlock.difficulty




def matchDifficuilty(h,difficulty) -> bool:
	upperbound = (1<< (256 - difficulty))
	h = int(h,16) #convert hex to int
	if h < upperbound:
		return True
	else:
		return False


def mineBlock(block):
	block.nonce = 0
	while True:
		h = block.calculate_hash()
		if matchDifficuilty(h,block.difficulty):
			#return new block with nonce
			block.hash = h
			return block
		block.nonce +=1



def generateBlock_with_data(data):
	prev_block = blockchain[-1]
	difficulty = getDifficulty()
	newIndex = prev_block.index +1
	newTime = int(time.time()) #sec
	newBlock_raw = Block(newIndex,data,newTime,'',prev_block.hash,0,difficulty)
	newBlock = mineBlock(newBlock_raw) #start mine block
	return newBlock


# print(generateBlock_with_data("hello"))

def generateNextBlock():
	pass



#=========validate block========
#block类型检查
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
        # raise ValueError('Invalid genesis block')
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

#valide a whole chain
def validate_blockchain(chain):
    """When given a blockchain, validates that all blocks are valid, raising
    a ValueError if an inconsistency or other problem is found"""
    if len(chain) < 1:
        # raise ValueError('Zero-length blockchain')
        return False
    if not validate_genesis_block(chain[0]):
    	return False
    for i in range(1, len(chain)):
        if not validate_block(chain[i], chain[i - 1]):
        	return False
    return True
    ##and validate transactions

# print(validate_blockchain([]))


#replace the chian with new chain if it's has more work
def replaceChain(newchain):
	if validate_blockchain(newchain):
		getAccumulatedDifficulty(blockchain) > getAccumulatedDifficulty(newchain):
		blockchain=newchain
		#setUtxos(utxo)
		#update tx pool
		#broadcast latest
		pass
	else:
		print("Received blockchain is invalid.")




# def matchDifficuilty(hash, difficulty)



def getAccumulatedDifficulty(chain):
	return sum([2**block.difficulty for block in chain])


# def isValidTimestamp():
# 	pass


# def addBlockToChain():
# 	pass

# def replaceChain():
# 	pass

