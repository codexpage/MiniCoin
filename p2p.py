from flask import Flask, jsonify
import pickle

app = Flask(__name__)

peers=[]

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
    return pickle.dumps({'tasks': tasks})

@app.route('/queryall', methods=['GET'])
def queryall():
    print(pickle.dumps({'tasks': tasks}))#bytes
    return pickle.dumps({'tasks': tasks})

if __name__ == '__main__':
    app.run(debug=True)