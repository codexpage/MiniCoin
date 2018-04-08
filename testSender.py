import chain
import p2p

res=p2p.getRequest("http://localhost:8001/queryall")
print(res[0])