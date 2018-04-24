import ecdsa
import os
import transaction
import utils

privateKeyPath = "./key/private_key"
priKey = ""


def getPrivateKeyFromWallet():
    # return utils.privatekey
    global priKey
    if priKey:
        return priKey
    else:
        with open(privateKeyPath, 'rb') as pri:
            # privateKey = pri.read()
            privateKey = ecdsa.SigningKey.from_string(
                pri.read(), curve=ecdsa.SECP256k1)
            pri.close()
            priKey = privateKey
        return privateKey


def getPubKeyFromWallet()->str:
    privateKey = getPrivateKeyFromWallet()
    return privateKey.get_verifying_key().to_string().hex()


def generatePrivateKey():
    signing_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
    return signing_key


def initWallet():
    if os.path.exists(privateKeyPath):
        return

    newPrivateKey = generatePrivateKey()
    with open(privateKeyPath, 'wb') as pri:
        pri.write(newPrivateKey.to_string())
        pri.close()


def deleteWallet():
    if os.path.exists(privateKeyPath):
        os.remove(privateKeyPath)


def getBalance(addr: str, utxos) -> int:
    balance = 0
    for outs in findTtxos(addr, utxos):
        balance += outs.amount
    return balance


def findTtxos(addr: str, unspentTxOuts):
    ret = []
    for outs in unspentTxOuts:
        if outs.address == addr:
            ret.append(outs)
    return ret


def findAmount(amount: int, unspentTxOuts):
    balance = 0
    find = []
    for out in unspentTxOuts:
        find.append(out)
        balance += out.amount
        if balance >= amount:
            changes = balance - amount
            return find, changes

    print("balance not enough")
    return None,None


def createTxOuts(receiverAddr: str, myAddr, amount, leftAmount):
    txOut = transaction.TxOut(receiverAddr, amount)
    if leftAmount == 0:
        return [txOut]
    else:
        changes = transaction.TxOut(myAddr, leftAmount)
        return [txOut, changes]


def createTx(receiver, amount, privateKey, unspentTxOuts, pool):
    myaddr = transaction.getPublicKey(privateKey)
    myUnsepnts = []
    for out in unspentTxOuts:
        if out.address == myaddr:
            myUnsepnts.append(out)

    myUnspentTxOut = filterTxPool(myUnsepnts, pool) #remove utxos which has been spent in the pool

    included, changes = findAmount(amount, myUnspentTxOut)
    if not included:
        return None

    unsigned = []
    for txout in included:
        unsigned.append(toUnsignedTxIn(txout))

    tx = transaction.Transaction('', unsigned, createTxOuts(receiver, myaddr, amount, changes))
    tx.id = transaction.getTxid(tx)

    for i in range(0, len(tx.txIns)):
        tx.txIns[i].signature = transaction.signTxin(tx, i, privateKey, unspentTxOuts)

    return tx


def toUnsignedTxIn(unspentTxOut):
    return transaction.TxIn(unspentTxOut.txOutId, unspentTxOut.txOutIndex,'')


def filterTxPool(unspentTxOuts, pool):
    # pass
    txIns = []
    for tx in pool:
        txIns.extend(tx.txIns)

    removeable = []
    for out in unspentTxOuts:
        for ins in txIns:
            if ins.txOutIndex == out.txOutIndex and ins.txOutId == out.txOutId:
                removeable.append(out)

    for rm in removeable:
        unspentTxOuts.remove(rm)
    return unspentTxOuts


if __name__ == '__main__':
    pass
