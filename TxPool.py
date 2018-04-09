import transaction
import copy
#list of txs
txPool =[]

def getTxPool():
    return copy.deepcopy(txPool)

def addToTxPool(tx: transaction, unspentTxOuts) -> bool:
    if not transaction.validateTx(tx, unspentTxOuts):
        # raise("invalid tx")
        return False
    if not isValidTxForPool(tx, txPool):
        # raise("invalid addtion")
        return False
    
    txPool.append(tx)
    return True

def hasTxIn(txIn: transaction.TxIn, unspentTxOut:[transaction.UnspentTxOut]):
    newTxIn = []
    for tx in unspentTxOut:
        if tx.txOutId == txIn.txOutId and tx.txOutIndex == txIn.txOutIndex:
            newTxIn.append(tx)
    return (newTxIn is not None)

def updateTxPool(unspentTxOuts: [transaction.UnspentTxOut]):
    invalidTxs = []
    for tx in txPool:
        for ins in tx.txIns:
            if not hasTxIn(ins, unspentTxOuts):
                invalidTxs.append(tx)
                break


    if len(invalidTxs) > 0:
        # transactionPool = _.without(transactionPool, ...invalidTxs);
        for invalid in invalidTxs:
            txPool.remove(invalid)


def getTxPoolIns(pool: [transaction.Transaction]):
    ret = []
    for p in pool:
        ret.extend(p.txIns)
    # return pool.map(lambda tx: tx.txIns).flatten().value()
    return ret

def isValidTxForPool(tx: transaction.Transaction, pool: [transaction.Transaction]):
    txPoolIns = getTxPoolIns(pool)


    for ins in tx.txIns:
        if containsTxIn(txPoolIns, ins):
            return False
    return True


def containsTxIn(txIns, txIn):
    # contains = True
    for ins in txIns:
        if txIn.txOutIndex == ins.txOutIndex and txIn.txOutId == ins.txOutId:
            return True
    return  False