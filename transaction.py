import utils
import ecdsa
import string
from functools import reduce
from wallet import getPrivateKeyFromWallet, getPubKeyFromWallet

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



# txin and txout content to string then sha256 to hash value(txid)
def getTxid(tx):
    txin_content = ''.join([txin.txOutId + str(txin.txOutIndex) for txin in tx.txIns])
    txout_content = ''.join([txout.address + str(txout.amount) for txout in tx.txOuts])
    return utils.sha256d(txin_content + txout_content)


def validateTx(tx: Transaction, unspentTxOuts):
    if not isValidTxStruct(tx):
        print("tx struct is not valid")
        return False

    if getTxid(tx) != tx.id:
        print("txid is not correct")
        return False

    hasValidTxIns = True
    for ins in tx.txIns:
        hasValidTxIns = hasValidTxIns and validateTxIn(ins, tx, unspentTxOuts)#all In should be valid

    if not hasValidTxIns:
        print("some txIn in the tx is not invalid ")
        return False

    totalTxInValue = 0
    for ins in tx.txIns:
        totalTxInValue += getTxInAmount(ins, unspentTxOuts)

    totalTxOutValue = 0
    for outs in tx.txOuts:
        totalTxOutValue += outs.amount

    if totalTxInValue != totalTxOutValue:
        print("txIn value not equal to txOut value")
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

    if hasDups(txIns):
        print("block contain dup txIn, cannot spend same txout twice.")
        return False

    validNormalTx = True
    for i in range(1, len(txs)): #every tx  should be valid (except coinbase tx)
        validNormalTx = validNormalTx and validateTx(txs[i], unspentTxOuts)
    return validNormalTx


def hasDups(txIns):
    if len(txIns) != len(set(txIns)):
        # if len(txIns) == set(txIns):
        return True
    return False


# input tx and block index
def validateCoinbaseTx(tx: Transaction, index: int) -> bool:
    return (
            tx is not None
            and getTxid(tx) == tx.id
            and len(tx.txIns) == 1
            and tx.txIns[0].txOutIndex == index  # special outindex for coinbase = block index
            and len(tx.txOuts) == 1
            and tx.txOuts[0].amount == COINBASE_AMOUNT  # TODO halve the subsidy
    )


def validateTxIn(txIn: TxIn, tx: Transaction, unspents):

    referencedTxOut=None

    for unspent in unspents:
        if unspent.txOutId == txIn.txOutId and unspent.txOutIndex == txIn.txOutIndex:
            referencedTxOut = unspent
            break

    if referencedTxOut is None:
        print("there is not matching txout in utxos for this txIn", txIn)
        return False

    pub = bytes.fromhex(referencedTxOut.address)
    key = ecdsa.VerifyingKey.from_string(string=pub, curve=ecdsa.SECP256k1)
    if not key.verify(bytes.fromhex(txIn.signature), tx.id.encode()):
        print("txin signature incorrect", txIn)
        return False
    return True


def getTxInAmount(txIn: TxIn, unspents):
    return findUnspentTxOut(txIn.txOutId, txIn.txOutIndex, unspents).amount


def findUnspentTxOut(txId, index, unspents):
    for unspent in unspents:
        if unspent.txOutId == txId and unspent.txOutIndex == index:
            return unspent

    return None


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

    key = getPrivateKeyFromWallet()
    signiture = key.sign(id.encode()).hex()  # .toDER().encode('hex')

    return signiture


def updateUnspentTxOut(txs, unspentTxout, index):
    newUnspentTxOut = []
    for tx in txs:
        txout = []
        for i in range(0, len(tx.txOuts)):
            txout.append(UnspentTxOut(tx.id, i, tx.txOuts[i].address, tx.txOuts[i].amount))

        newUnspentTxOut = newUnspentTxOut + txout
    consumedTxOuts = []
    newTxIns = []
    for tx in txs:
        newTxIns += tx.txIns

    for ins in newTxIns:
        consumedTxOuts.append(UnspentTxOut(ins.txOutId, ins.txOutIndex, '', 0))


    result = []
    for unspent in unspentTxout:
        if not findUnspentTxOut(unspent.txOutId, unspent.txOutIndex, consumedTxOuts):
            result.append(unspent)
    result += newUnspentTxOut
    return result


def processTx(txs, unspentTxout, blockIndex):
    if not isValidTxList(txs):
        print("tx in block is invalid")
        return None
    if not validateBlockTxs(txs, unspentTxout, blockIndex):
        print("tx dups or invlid coinbase")
        return None
    return updateUnspentTxOut(txs, unspentTxout, blockIndex)




def getPublicKey(privatekey) -> str:
    return privatekey.get_verifying_key().to_string().hex()


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
            and isinstance(tx.txOuts, list)
            and validateOut
    )

