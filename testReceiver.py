
from flask import Flask, jsonify,request
import pickle
import  requests
import  threading
import  time
app = Flask(__name__)


@app.route('/block', methods=['GET'])
def receiveBlock():
    # content = request.get_data()
    # print(content)
    # obj = pickle.loads(content)
    # print(obj)
    print("receive")
    getRequest("http://localhost:8001/block")
    time.sleep(2)

    # th.start()
    print("sended.")
    return "ok"

def getRequest(url):
    # time.sleep(5)
    print("send get")
    r = requests.get(url)
    print(r.content)
    return "ok"


if __name__ == '__main__':
    # th = threading.Thread(target=getRequest, args=("http://localhost:8001/block",), daemon=True)
    app.run(debug=False, host='0.0.0.0', port=8002)