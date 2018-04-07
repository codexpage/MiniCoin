import rsa
import utils
import string
from functools import reduce


# use rsa2048 (2048bit) instead of dsa

COINBASE_AMOUNT = 50


class UnspentTxOut:
    def __init__(self, txOutId: str, txOutIndex: int, address: str, amount: int):
        self.txOutId = txOutId
        self.txOutIndex = txOutIndex
        self.address = address
        self.amount = amount


class TxIn:
    def __init__(self, txOutId: str, txOutIndex: int, signature: str):
        self.txOutId = txOutId
        self.txOutIndex = txOutIndex
        self.signature = signature


class TxOut:
    def __init__(self, address: str, amount: int):
        self.address = address
        self.amount = amount


class Transaction:
    def __init__(self, id: str, txIns, txOuts):
        self.id = id
        self.txIns = txIns  # list
        self.txOuts = txOuts

# def __getattr__(self, item):
# 	return self.item


# txin and txout content to string then sha256 to hash value(txid)
def getTxid(tx):
    txin_content = ''.join([txin.txOutId + str(txin.txOutIndex) for txin in tx.txIns])
    txout_content = ''.join([txout.address + str(txout.amount) for txout in tx.txOuts])
    return utils.sha256d(txin_content + txout_content)



def validateTx(tx: Transaction, unspentTxOuts):
    if getTxid(tx) != tx.id:
        return False

    hasValidTxIns = tx.txIns.map(lambda t: validateTxIn(t, tx, unspentTxOuts)).reduce(lambda t1, t2: t1 and t2, True)

    if not hasValidTxIns:
        return False

    totalTxInValue = tx.txIns.map(lambda t: getTxInAmount(t, unspentTxOuts)).reduce(lambda t1, t2: t1 + t2, 0)

    totalTxOutValue = tx.txOuts.map(lambda t: t.amount).reduce(lambda t1, t2: t1 + t2, 0)

    if totalTxInValue != totalTxOutValue:
        return False
    return True


def validateBlockTxs(txs, unspentTxOuts, index):
    coinbaseTx = txs[0]
    if not validateCoinbaseTx(coinbaseTx, index):
        return False

#     // check
#     for duplicate txIns.Each txIn can be included only once
#     const
#     txIns: TxIn[] = _(aTransactions)
#     .map(tx= > tx.txIns)
#     .flatten()
#     .value();
#
#
# if (hasDuplicates(txIns)) {
# return false;
# }
    txIns = txs.map(lambda tx: txIns).flatten().value()
    if hasDups(txIns):
        return False

    normalTx = txs.slice(1)
    return normalTx.map(lambda tx: validateTx(tx, unspentTxOuts)).recude(lambda t1, t2: t1 and t2, True)


# TODO
def hasDups(txIns):
    # groups = _.countBy(txIns, (txIn) = > txIn.txOutId + txIn.txOutId);
    # return _(groups)
    # .map((value, key) = > {
    # if (value > 1)
    # {
    #     console.log('duplicate txIn: ' + key);
    # return true;
    # } else {
    # return false;
    pass

def validateCoinbaseTx(tx: Transaction, index: int) -> bool:
    return (
        tx is not None
        and getTxid(tx) == tx.id
        and len(tx.txIns) == 1
        and tx.txIns[0].txOutIndex == index
        and len(tx.txOuts) == 1
        and tx.txOuts[0].amount == COINBASE_AMOUNT
    )


def validateTxIn(txIn: TxIn, tx: Transaction, unspents):
    referencedTxOut = unspents.find(lambda t: t.txOutId == txIn.txOutId and t.txOutId == txIn.txOutId)
    if referencedTxOut is None:
        return False
    addr = referencedTxOut.address


    # key = ""

    # key = ec.keyFromPublic(address, 'hex');
    # return key.verify(transaction.id, txIn.signature);
    return rsa.verify(tx.id, txIn.signature, utils.pubkey)


def getTxInAmount(txIn: TxIn, unspents):
    return findUnspentTxOut(txIn.txOutId, txIn.txOutIndex, unspents).amount

def findUnspentTxOut(txId, index, unspents):
    return unspents.find(lambda t: t.txOutId == txId and t.txOutIndex == index)


def getCoinbaseTx(addr: str, index: int):
    txIn = TxIn("", index,"")
    t = Transaction('',[txIn],[TxOut(addr, COINBASE_AMOUNT)])
    t.id = getTxid(t)
    return t


def signTxin(tx: Transaction, txInIndex: int, pk: str, unspentTxOuts) -> str:
    txIn = tx.txIns[txInIndex]

    id = tx.id
    referred = findUnspentTxOut(txIn.txOutId, txIn.txOutIndex, unspentTxOuts)
    if referred is None:
        raise ("could not find referenced txout")
    addr = referred.address
    if getPublicKey(pk) != addr:
        raise ("input does not match")

    # TODO key
    # key = toHex(utils.privatekey)
    # signature = toHex(rsa.encrypt(id, pk))

    return rsa.sign(id, utils.privatekey)




def updateUnspentTxOut(txs, unspentTxout):
    newUnspentTxOut = reduce(lambda t1, t2: t1 + t2 ,
                             map(lambda tx:
                                 map(lambda txout, index: UnspentTxOut(tx.id, index, txout.address, txout.amount),
                                     tx.txOuts),
                                 txs))
    consumedTxOuts = map(lambda txin: UnspentTxOut(txin.txOutId, txin.txOutIndex, "", 0) ,
                         reduce(lambda t1, t2: t1+ t2,
                                map(lambda tx: tx.txIns,
                                    txs)))

    result = filter(lambda tx: not findUnspentTxOut(tx.txOutsId, tx.txOutsIndex, consumedTxOuts), unspentTxout) \
             + newUnspentTxOut

def processTx(txs, unspentTxout, blockIndex):
    if not isValidTxList(txs):
        return None
    if not validateBlockTxs(txs, unspentTxout, blockIndex):
        return None
    return updateUnspentTxOut(txs, unspentTxout)


# def toHex(byte):
#     pass


def getPublicKey(privatekey: str) -> str:
#     rsa.construct()
    pass

def isValidTxIn(txin: TxIn) -> bool:
    return (
            txin is not None
            and type(txin.signature) == str
            and type(txin.txOutId) == str
            and type(txin.txOutIndex) == int
    )


def isValidTxOut(txout: TxOut) -> bool:
    return (
        txout is not None
        and type(txout.address) == str
        and isValidAddr(txout.address)
        and type(txout.amount) == int
    )


def isValidAddr(address: str) -> bool:
    if len(address) != 256:
        print("invalid public key length")
        return False
    elif not all(c in string.hexdigits for c in address):
        print("public key must contain only hex characters")
        return False
    return True

def isValidTxList(txs) -> bool:
    return reduce(lambda tx1, tx2: tx1 and tx2, map(lambda tx: isValidTxStruct(tx), txs))

def isValidTxStruct(tx: Transaction) -> bool:
    return (
            type(tx.id) == str
            and isinstance(tx.txIns, list)
            and reduce(lambda t1, t2: t1 and t2, map(lambda txin: isValidTxIn(txin), tx.txIns))
            and isinstance(tx.txOuts, list)
            and reduce(lambda t1, t2: t1 and t2, map(lambda txout: isValidTxOut(txout), tx.txOuts))
    )


# def updateUtxos(txs, utxo):
#     # return new utxo list
#     return []
#
#
# #
# def processTxs(txs, utxo, blockIndex: int):
#     # validate block tx
#     # update utxo
#     # retuurn
#     pass
