from flask import Flask, jsonify
import pickle
import requests

app = Flask(__name__)

selfip = ""
peers=[] #read from file list of ip 

tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol', 
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web', 
        'done': False
    }
]

@app.route('/querylast', methods=['GET'])
def querylast():
    print(pickle.dumps({'tasks': tasks}))#bytes
    return jsonify({'tasks': tasks})

@app.route('/queryall', methods=['GET'])
def queryall():
    print(pickle.dumps({'tasks': tasks}))#bytes
    return jsonify({'tasks': tasks})

@app.route('/querytx', methods=['GET'])
def querytx():
    print(pickle.dumps({'tasks': tasks}))#bytes
    return jsonify({'tasks': tasks})

# r = requests.post("http://bugs.python.org", data={'number': 12524, 'type': 'issue', 'action': 'show'})

def getRequest(url) -> dict:
    r = requests.get(url)
    return r.json()

def postRequest(url, data) -> dict:
    r = requests.post(url, data)
    return r.json()

if __name__ == '__main__':
    app.run(debug=True)
