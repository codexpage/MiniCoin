# import rsa
import utils
import ecdsa
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

    def __eq__(self, other):
        return (
                self.txOutId == other.txOutId
                and self.txOutIndex == other.txOutIndex
                and self.address == other.address
                and self.amount == other.amount
        )


class TxIn:
    def __init__(self, txOutId: str, txOutIndex: int, signature: str):
        self.txOutId = txOutId
        self.txOutIndex = txOutIndex
        self.signature = signature

    def __eq__(self, other):
        return (
                self.txOutId == other.txOutId
                and self.txOutIndex == other.txOutIndex
                and self.signature == other.signature
        )

    def __hash__(self):
        return hash(frozenset(self.__dict__.items()))


class TxOut:
    def __init__(self, address: str, amount: int):
        self.address = address
        self.amount = amount

    def __eq__(self, other):
        return (
            self.address == other.address
            and self.amount == other.amount
        )


class Transaction:
    def __init__(self, id: str, txIns, txOuts):
        self.id = id
        self.txIns = txIns  # [TxIn]
        self.txOuts = txOuts # [TxOut]
    def __eq__(self, other):
        return (
            self.id == other.id
            and self.txIns == other.txIns #compare two list
            and self.txOuts == other.txOuts
        )


# def __getattr__(self, item):
# 	return self.item


# txin and txout content to string then sha256 to hash value(txid)
def getTxid(tx):
    txin_content = ''.join([txin.txOutId + str(txin.txOutIndex) for txin in tx.txIns])
    txout_content = ''.join([txout.address + str(txout.amount) for txout in tx.txOuts])
    return utils.sha256d(txin_content + txout_content)


def validateTx(tx: Transaction, unspentTxOuts):
    if not isValidTxStruct(tx):
        return False

    if getTxid(tx) != tx.id:
        return False

    # hasValidTxIns = tx.txIns.map(lambda t: validateTxIn(t, tx, unspentTxOuts)).reduce(lambda t1, t2: t1 and t2, True)
    hasValidTxIns = True
    for ins in tx.txIns:
        hasValidTxIns = hasValidTxIns and validateTxIn(ins, tx, unspentTxOuts)

    if not hasValidTxIns:
        return False

    # totalTxInValue = tx.txIns.map(lambda t: getTxInAmount(t, unspentTxOuts)).reduce(lambda t1, t2: t1 + t2, 0)
    totalTxInValue = 0
    for ins in tx.txIns:
        totalTxInValue += getTxInAmount(ins, unspentTxOuts)

    # totalTxOutValue = tx.txOuts.map(lambda t: t.amount).reduce(lambda t1, t2: t1 + t2, 0)
    totalTxOutValue = 0
    for outs in tx.txOuts:
        totalTxOutValue += outs.amount

    if totalTxInValue != totalTxOutValue:
        return False

    return True


def validateBlockTxs(txs, unspentTxOuts, index):
    coinbaseTx = txs[0]
    if not validateCoinbaseTx(coinbaseTx, index):
        print("invalid coinbase tx")
        return False

    txIns = []
    for tx in txs:
        txIns += tx.txIns

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
    #     txIns = txs.map(lambda tx: txIns).flatten().value()
    if hasDups(txIns):
        # print("dups")
        return False

    # normalTx = txs.slice(1)
    validNormalTx = True
    for i in range(1, len(txs)):
        validNormalTx = validNormalTx and validateTx(txs[i], unspentTxOuts)
    # return normalTx.map(lambda tx: validateTx(tx, unspentTxOuts)).recude(lambda t1, t2: t1 and t2, True)
    return validNormalTx


def hasDups(txIns):
    if len(txIns) != len(set(txIns)):
        print
        # if len(txIns) == set(txIns):
        return True
    return False
    # groups = _.countBy(txIns, (txIn) = > txIn.txOutId + txIn.txOutId);
    # return _(groups)
    # .map((value, key) = > {
    # if (value > 1)
    # {
    #     console.log('duplicate txIn: ' + key);
    # return true;
    # } else {
    # return false;
    # pass


# input tx and block index
def validateCoinbaseTx(tx: Transaction, index: int) -> bool:
    # print(getTxid(tx),tx.id)
    return (
            tx is not None
            and getTxid(tx) == tx.id
            and len(tx.txIns) == 1
            and tx.txIns[0].txOutIndex == index  # special outindex for coinbase = block index
            and len(tx.txOuts) == 1
            and tx.txOuts[0].amount == COINBASE_AMOUNT  # TODO halve the subsidy
    )


def validateTxIn(txIn: TxIn, tx: Transaction, unspents):
    # referencedTxOut =

    # referencedTxOut = unspents.find(lambda t: t.txOutId == txIn.txOutId and t.txOutId == txIn.txOutId)

    for unspent in unspents:
        if unspent.txOutId == txIn.txOutId and unspent.txOutIndex == txIn.txOutIndex:
            referencedTxOut = unspent
            break

    if referencedTxOut is None:
        return False

    # public key
    addr = referencedTxOut.address
    key = ecdsa.VerifyingKey.from_string(string=addr, curve=ecdsa.SECP256k1)
    # key = ecdsa.keyFromPublic(addr, 'hex')
    # ecdsa.verify(tx.id, txIn.signature)
    # key = ""
    return key.verify(tx.id, txIn.signature)
    # key = ec.keyFromPublic(address, 'hex');
    # return key.verify(transaction.id, txIn.signature);
    # return rsa.verify(tx.id, txIn.signature, utils.pubkey)


def getTxInAmount(txIn: TxIn, unspents):
    return findUnspentTxOut(txIn.txOutId, txIn.txOutIndex, unspents).amount


def findUnspentTxOut(txId, index, unspents):
    for unspent in unspents:
        if unspent.txOutId == txId and unspent.txOutIndex == index:
            return unspent

    return None
    # return unspents.find(lambda t: t.txOutId == txId and t.txOutIndex == index)


def getCoinbaseTx(addr: str, index: int):
    txIn = TxIn("", index, "")
    t = Transaction('', [txIn], [TxOut(addr, COINBASE_AMOUNT)])
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
    # key = ecdsa.keyFromPrivate(pk, 'hex')
    key = ecdsa.SigningKey.from_string(string=pk, curve=ecdsa.SECP256k1)
    signiture = key.sign(id).hex()  # .toDER().encode('hex')

    # key = toHex(utils.privatekey)
    # signature = toHex(rsa.encrypt(id, pk))

    return signiture


def updateUnspentTxOut(txs, unspentTxout):
    newUnspentTxOut = []
    for tx in txs:
        txout = []
        for i in range(0, len(tx.txOuts)):
            txout.append(UnspentTxOut(tx.id, i, tx.txOuts[i].address, tx.txOuts[i].amount))
        newUnspentTxOut = newUnspentTxOut + txout

    # newUnspentTxOut = reduce(lambda t1, t2: t1 + t2 ,
    #                          map(lambda tx:
    #                              map(lambda txout, index: UnspentTxOut(tx.id, index, txout.address, txout.amount),
    #                                  tx.txOuts),
    #                              txs))
    consumedTxOuts = []
    newTxIns = []
    for tx in txs:
        newTxIns += tx.txIns

    for ins in newTxIns:
        consumedTxOuts.append(UnspentTxOut(ins.txOutId, ins.txOutIndex, '', 0))

    # consumedTxOuts = map(lambda txin: UnspentTxOut(txin.txOutId, txin.txOutIndex, "", 0) ,
    #                      reduce(lambda t1, t2: t1+ t2,
    #                             map(lambda tx: tx.txIns,
    #                                 txs)))

    result = []
    for unspent in unspentTxout:
        if not findUnspentTxOut(unspent.txOutId, unspent.txOutIndex, consumedTxOuts):
            result.append(unspent)
    result += newUnspentTxOut
    return result
    # result = filter(lambda tx: not findUnspentTxOut(tx.txOutsId, tx.txOutsIndex, consumedTxOuts), unspentTxout) \
    #          + newUnspentTxOut


def processTx(txs, unspentTxout, blockIndex):
    if not isValidTxList(txs):
        print("tx in block is invalid")
        return None
    if not validateBlockTxs(txs, unspentTxout, blockIndex):
        print("tx dups or invlid coinbase")
        return None
    return updateUnspentTxOut(txs, unspentTxout)


# def toHex(byte):
#     pass


def getPublicKey(privatekey: str) -> str:
    #     rsa.construct()
    return ecdsa.SigningKey().from_string(privatekey, curve=ecdsa.SECP256k1).get_verifying_key().hex()

    # return ecdsa.keyFromPrivate(privatekey, 'hex').getPublic().encode('hex')
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
    if len(address) != 128:
        print("invalid public key length")
        return False
    elif not all(c in string.hexdigits for c in address):
        print("public key must contain only hex characters")
        return False
    return True


def isValidTxList(txs) -> bool:
    return reduce(lambda tx1, tx2: tx1 and tx2, map(lambda tx: isValidTxStruct(tx), txs))


def isValidTxStruct(tx: Transaction) -> bool:
    validateIn = True
    for ins in tx.txIns:
        validateIn = validateIn and isValidTxIn(ins)

    validateOut = True
    for outs in tx.txOuts:
        validateOut = validateOut and isValidTxOut(outs)
    return (
            type(tx.id) == str
            and isinstance(tx.txIns, list)
            and validateIn
            # and reduce(lambda t1, t2: t1 and t2, map(lambda txin: isValidTxIn(txin), tx.txIns))
            and isinstance(tx.txOuts, list)
            and validateOut
        # and reduce(lambda t1, t2: t1 and t2, map(lambda txout: isValidTxOut(txout), tx.txOuts))
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
