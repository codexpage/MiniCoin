import chain
# import p2p
#
# res=p2p.getRequest("http://localhost:8001/queryall")
# print(res[0])



from flask import Flask, jsonify,request
import pickle
import  requests
app = Flask(__name__)
import threading


@app.route('/block', methods=['GET'])
def receiveBlock():
    # content = request.get_data()
    # print(content)
    # obj = pickle.loads(content)
    # print(obj)
    print("receive data")
    return "data"

def getRequest(url):
    print("send..")
    r = requests.get(url)
    print("get.")
    print(r.content)
    return "ok"


def server():
    app.run(debug=False, host='0.0.0.0', port=8001)
if __name__ == '__main__':
    th = threading.Thread(target=server, daemon=True)
    th.start()
    getRequest("http://localhost:8002/block")
    th.join()

