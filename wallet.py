import utils


privateKeyPath = "./private_key"

def getPrivateKeyFromWallet() -> str:
	return utils.privatekey
	# pass
	#read from file private_key
	#return the string


def getPubKeyFromWallet():
	return utils.pubkey
	# pass
	#return calpub(private_key)


# def generatePrivateKey()->str:
# 	pass
	#use the lib to gen key pair
	#return pri str

def initWallet():#gen pri key file
	pass
	#check private_key 
	#if not exist 
	#gen pri key
	#write to file
	#print

#input wallet addr and current utxos, return balance
def getBalance(addr:str, utxos)-> int:
	pass


def findTtxos():
	pass


#return list of TxOut
def createTxOuts(receiverAddr:str, myAddr,amount, leftAmount):
	pass

def createTx():
	pass


def fileterTxPool():
	pass
	

#return a Tx
def createTransaction(receiverAddr:str, amount:int, privateKey:str, utxos, txPool):
	pass




