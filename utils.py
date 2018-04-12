import hashlib

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
peers=[] #read from file list of ip

#TODO read url filter url ,build peer list
def readUrlfromFile():
    #fill peerip TODO read ip from file
    global peers
    global selfport
    # li = ["http://localhost:8001","http://localhost:8002"]
    li = []
    base = "http://localhost"
    for p in range (8000, 8050):
        li.append(base + ":" + str(p))
    li.remove(selfip)#remove selfip
    peers = li
    selfport = selfip[-4:]
    return




if __name__ == '__main__':
    main()
