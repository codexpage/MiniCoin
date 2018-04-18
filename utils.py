import hashlib
import random
import copy
import os
import pickle
# import rsa
# (privatekey, pubkey) = rsa.newkeys(2048)


def sha256d(s: [str, bytes]) -> str:  # 加密hash
    """A double SHA-256 hash."""
    if not isinstance(s, bytes):
        s = s.encode()  # to bytes

    # return hashlib.sha256(hashlib.sha256(s).digest()).hexdigest()
    return hashlib.sha256(s).hexdigest()


# convert bytes to hex string
# use hexdigest
# covnert form string to bytes
# use encode

# serialization
# we use pickle or json to seialize and deseialize


def main():
    print(sha256d("hello world"))


def list_hash(to_hash) -> str:
    """Calculates the hash for a block that would contain the passed attributes"""
    to_hash = ''.join(to_hash)
    # to_hash = str(index) + str(prev_hash) + str(timestamp) + data
    to_hash = to_hash.encode('utf-8')
    return sha256d(to_hash)


selfip = ""
selfport =""
peerList = "./peerlist/peersto"
peers=[] #read from file list of ip
live = []
everContact = []
#TODO read url filter url ,build peer list
def readUrlfromFile():
    #fill peerip TODO read ip from file
    global peers
    global selfport
    global live
    global everContact
    if os.path.exists(peerList) and os.path.getsize(peerList) > 0:
        everContact = list(pickle.load(open(peerList, "rb")))
# bugs temporary solution
#         if '.' in peers:
#             everContact = []
        if selfip in everContact:
            everContact.remove(selfip)
            live = copy.deepcopy(everContact)
    else:

    # if selfip
    # li = ["http://localhost:8001","http://localhost:8002"]
        li = []
        base = "http://localhost"
        for p in range (8001, 8010):
            li.append(base + ":" + str(p))
        li.remove(selfip)#remove selfip
        peers = li
        live = copy.deepcopy(peers)


        random.shuffle(peers)
    # everContact = copy.deepcopy(peers)
    selfport = selfip[-4:]
    return




if __name__ == '__main__':
    main()
