import hashlib

def sha256d(s:[str, bytes]) -> str: #加密hash
    """A double SHA-256 hash."""
    if not isinstance(s, bytes):
        s = s.encode() #to bytes

    # return hashlib.sha256(hashlib.sha256(s).digest()).hexdigest()
    return hashlib.sha256(s).hexdigest()


#convert bytes to hex string
#use hexdigest
#covnert form string to bytes
#use encode

#serialization
#we use pickle or json to seialize and deseialize





#use secp256k1
def getPubKey(privateKey: str) -> str:
	pass

def getCurrentTimestamp() -> int :
	#get tie 
	pass

def main():
	print(sha256d("hello world"))

def list_hash(to_hash) -> str:
    """Calculates the hash for a block that would contain the passed attributes"""
    to_hash = ''.join(to_hash)
    # to_hash = str(index) + str(prev_hash) + str(timestamp) + data
    to_hash = to_hash.encode('utf-8')
    return sha256d(to_hash)

if __name__ == '__main__':
	main()