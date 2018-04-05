import ecdsa
from base58 import b58encode_check
import utils

COINBASE_AMOUNT = 50

class UnspentTxOut:
	def __init__(self, txOutId:str, txOutIndex:int, address:str, amount:int):
		self.txOutId = txOutId
		self.txOutIndex = txOutIndex
		self.address = address
		self.amount = amount


class TxIn:
 	def __init__(self, txOutId:str, txOutIndex:int, signature:str):
 		self.txOutId = txOutId
 		self.txOutIndex = txOutIndex
 		self.signature = signature


class TxOut:
	def __init__(self, address:str, amount:int):
		self.address = address
		self.amount = amount
 
class Transaction:
	def __init__(self, id: str, txIns, txOuts):
		self.id = id
		self.txIns = txIns #list
		self.txOuts = txOuts 


#txin and txout content to string then sha256 to hash value(txid)
def getTxid(tx):
	txin_content = ''.join([txin.txOutId + str(txin.txOutIndex) for txin in tx.txIns])
	txout_content = ''.join([txout.address + str(txout.amount) for txout in tx.txOuts])
	return sha256d(txin_content+txout_content)




def validate_tx_types(tx)->bool:
	pass

def validateTxIn_types(txin) -> bool:
	pass

def validateTxOut_types(txout) -> bool:
	pass

# valid address is a valid ecdsa public key in the 04 + X-coordinate + Y-coordinate format
def isvalidAddr(address:str) ->bool:
	pass


def updateUtxos(txs, utxo):
	#return new utxo list
	return []
#
def processTxs(txs, utxo, blockIndex:int):
	#validate block tx
	#update utxo
	#retuurn 
	pass




