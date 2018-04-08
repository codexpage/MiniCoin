# import utils
import ecdsa
import os
import transaction

privateKeyPath = "./private_key"
# EC = ecdsa.ecdsa('secp256k1')


# prik = "privateKey"
# pubk = "publicKey"

def getPrivateKeyFromWallet():
    # return utils.privatekey
    with open(privateKeyPath, 'rb') as pri:
        # privateKey = pri.read()
        privateKey = ecdsa.SigningKey.from_string(
            pri.read(), curve=ecdsa.SECP256k1)
        pri.close()
    return privateKey


# pass
# read from file private_key
# return the string


def getPubKeyFromWallet()->str:
    # return utils.pubkey
    privateKey = getPrivateKeyFromWallet()
    # key = EC.keyFromPrivate(privateKey, 'hex')
    # return key.getPublic().encode('hex')
    return privateKey.get_verifying_key().to_string().hex()



# pass
# return calpub(private_key)
def generatePrivateKey():
    # keyPair = EC.genKeyPair()
    # privateKey = keyPair.getPrivate()
    # return privateKey.encode('hex')
    signing_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
    return signing_key


# def generatePrivateKey()->str:
# 	pass
# use the lib to gen key pair
# return pri str

def initWallet():  # gen pri key file
    # pass
    if os.path.exists(privateKeyPath):
        return

    newPrivateKey = generatePrivateKey()
    with open(privateKeyPath, 'wb') as pri:
        pri.write(newPrivateKey.to_string())
        pri.close()


def deleteWallet():
    if os.path.exists(privateKeyPath):
        os.remove(privateKeyPath)


# check private_key
# if not exist
# gen pri key
# write to file
# print

# input wallet addr and current utxos, return balance
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
        balance += out.amout
        if balance >= amount:
            changes = balance - amount
            return find, changes

    raise ("balance not enough")


# return list of TxOut


def createTxOuts(receiverAddr: str, myAddr, amount, leftAmount):
    # pass
    txOut = transaction.TxOut(receiverAddr, amount)
    if leftAmount == 0:
        return [txOut]
    else:
        changes = transaction.TxOut(myAddr, leftAmount)
        return [txOut, changes]


def createTx(receiver, amount, privateKey, unspentTxOuts, pool):
    # pass
    myaddr = transaction.getPublicKey(privateKey)
    myUnsepnts = []
    for out in unspentTxOuts:
        if out.address == myaddr:
            myUnsepnts.append(out)

    myUnspentTxOut = filterTxPool(myUnsepnts, pool)

    included, changes = findTtxos(amount, myUnspentTxOut)

    unsigned = []
    for txout in included:
        unsigned.append(toUnsignedTxIn(txout))

    tx = transaction.Transaction('', unsigned, createTxOuts(receiver, myaddr, amount, changes))
    tx.id = transaction.getTxid(tx)

    for i in range(0, len(tx.txIns)):
        tx.txIns[i].signature = transaction.signTxin(tx, i, privateKey, unspentTxOuts)

    return tx


def toUnsignedTxIn(unspentTxOut: transaction.UnspentTxOut):
    return transaction.TxIn(unspentTxOut.txOutId, unspentTxOut.txOutIndex)


def filterTxPool(unspentTxOuts, pool: [transaction.Transaction]):
    # pass
    txIns = []
    for ins in pool:
        txIns.append(ins.txIns)

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
    # initWallet()
    # print(getPrivateKeyFromWallet().to_string().hex())
    # print(getPubKeyFromWallet())
