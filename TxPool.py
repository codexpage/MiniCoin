import transaction
import copy
#list of txs
txPool : transaction.Transaction =[]

def getTxPool():
    return copy.deepcopy(txPool)

def addToTxPool(tx: transaction, unspentTxOuts):
    if not transaction.validateTx(tx, unspentTxOuts):
        raise("invalid tx")

    if not isValidTxForPool(tx, txPool):
        raise("invalid addtion")

    txPool.append(tx)


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
    return pool.map(lambda tx: tx.txIns).flatten().value()


def isValidTxForPool(tx: transaction.Transaction, pool: [transaction.Transaction]):
    txPoolIns = getTxPoolIns()


    # TODO
    # const
    # containsTxIn = (txIns: TxIn[], txIn: TxIn) = > {
    # return _.find(txPoolIns, ((txPoolIn) = > {
    # return txIn.txOutIndex === txPoolIn.txOutIndex & & txIn.txOutId == = txPoolIn.txOutId;
    # }));
    # };

    for ins in tx.txIns:
        if containsTxIn(txPoolIns, ins):
            return False
    return True


def containsTxIn():
    pass