import requests
from flask import Flask, request
from argparse import ArgumentParser
from node import *
from flask_cors import CORS
from flask import jsonify

app = Flask(__name__)
CORS(app)
app.config['node_id'] = 0

# def positive_int(value):
#     ivalue = int(value)
#     if ivalue <= 0:
#         raise argparse.ArgumentTypeError("%s is not a positive integer" % value)
#     return ivalue

@app.route('/node-id')
def get_node_id():
    node_id = app.config['node_id']  # app.config.get('NEXT_NODE_ID', 0)
    app.config['node_id'] = node_id + 1
    response = jsonify({"node_id": node_id})
    return response
    #return str(node_id)


if __name__ == '__main__':
    # app.run(debug=True)

    parser = ArgumentParser()
    parser.add_argument('--ip', default='127.0.0.1', type = str)
    parser.add_argument('--port', default='5000', type=str)
    parser.add_argument('--bootstrap_ip', default='127.0.0.1', type=str)
    parser.add_argument('--bootstrap_port', default='5000', type=str)
    parser.add_argument('--is_bootstrap', type=int, choices=[0, 1], default=0)
    # parser.add_argument('--capacity', default=5000, type=positive_int)
    parser.add_argument('--capacity', default='5000', type=int)
    parser.add_argument('--difficulty', default=3, type=int)

    args = parser.parse_args()
    if args.capacity <= 0:
        print('Capacity must be a positive integer! Continuing with the default value of 5.')

    ip_address = args.ip
    port = args.port
    bootstrap_ip_address = args.bootstrap_ip
    bootstrap_port = args.bootstrap_port
    is_bootstrap = args.is_bootstrap
    capacity = args.capacity
    difficulty = args.difficulty



    node = Node(ip_address, port, bootstrap_ip_address, bootstrap_port, blockchain_snapshot = None, key_length = 2048)
    app.run(host='0.0.0.0', port=5000, debug = True )

#node = Node()
#app.config['node'] = node