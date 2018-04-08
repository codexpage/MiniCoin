
from flask import Flask, jsonify,request
import pickle
app = Flask(__name__)


@app.route('/block', methods=['POST'])
def receiveBlock():
    content = request.get_data()
    # print(content)
    obj = pickle.loads(content)
    print(obj)
    return "ok"


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8002)