import transaction
import copy
txPool =[]

def getTxPool():
    return copy.deepcopy(txPool)

def addToTxPool(tx: transaction, unspentTxOuts) -> bool:
    if not transaction.validateTx(tx, unspentTxOuts):
        return False
    if not isValidTxForPool(tx, txPool):
        return False
    
    txPool.append(tx)
    return True

def hasTxIn(txIn: transaction.TxIn, unspentTxOut:[transaction.UnspentTxOut]):
    newTxIn = []
    for utxo in unspentTxOut:
        if utxo.txOutId == txIn.txOutId and utxo.txOutIndex == txIn.txOutIndex:
            newTxIn.append(utxo)
    return not(newTxIn==[])

def updateTxPool(unspentTxOuts: [transaction.UnspentTxOut]):
    invalidTxs = []
    for tx in txPool:
        for txin in tx.txIns:
            if not hasTxIn(txin, unspentTxOuts):
                invalidTxs.append(tx)
                break


    if len(invalidTxs) > 0:
        for invalid in invalidTxs:
            txPool.remove(invalid)


def getTxPoolIns(pool: [transaction.Transaction]):
    ret = []
    for p in pool:
        ret.extend(p.txIns)
    return ret

def isValidTxForPool(tx: transaction.Transaction, pool: [transaction.Transaction]):
    txPoolIns = getTxPoolIns(pool)

    for ins in tx.txIns:
        if containsTxIn(txPoolIns, ins):
            return False
    return True


def containsTxIn(txIns, txIn):
    for ins in txIns:
        if txIn.txOutIndex == ins.txOutIndex and txIn.txOutId == ins.txOutId:
            return True
    return  False