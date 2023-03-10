import requests
from flask import Flask, request
from argparse import ArgumentParser
from node import *
from flask_cors import CORS
from flask import jsonify
import threading

app = Flask(__name__)
CORS(app)
app.config['node_id'] = 1
app.config['transaction_id'] = 1
app.config['nodes_details'] = dict()
app.config['node_counter'] = 1
app.config['transaction_output_id'] = 1
parser = ArgumentParser()
parser.add_argument('--ip', default='127.0.0.1', type=str)
parser.add_argument('--port', default='5000', type=str)
parser.add_argument('--bootstrap_ip', default='127.0.0.1', type=str)
parser.add_argument('--bootstrap_port', default='5000', type=str)
parser.add_argument('--is_bootstrap', type=int, choices=[0, 1], default=0)
# parser.add_argument('--capacity', default=5000, type=positive_int)
parser.add_argument('--capacity', default='5000', type=int)
parser.add_argument('--difficulty', default=3, type=int)
parser.add_argument('--no_nodes', default=3, type=int)

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
no_nodes = args.no_nodes

node = Node(ip_address, port, bootstrap_ip_address, bootstrap_port, no_nodes, blockchain_snapshot=None,
            key_length=2048)
app.run(host='0.0.0.0', port=5000, debug=True)


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
    # return str(node_id)


@app.route('/transaction-id')
def get_transaction_id():
    transaction_output_id = app.config['transaction_output_id']  # app.config.get('NEXT_NODE_ID', 0)
    app.config['transaction_output_id'] = transaction_output_id + 1
    response = jsonify({"transaction_output_id": transaction_output_id})
    return response

@app.route('/transaction-output-id')
def get_transaction_id():
    transaction_id = app.config['transaction_id']  # app.config.get('NEXT_NODE_ID', 0)
    app.config['transaction_id'] = transaction_id + 1
    response = jsonify({"transaction_id": transaction_id})
    return response

@app.route('/reduce-transaction-output-id')
def get_transaction_id():
    app.config['transaction_output_id']-=1
    return jsonify({'status': 'success'})


@app.route('/receive-network', method=['POST'])
def receive_network():
    all_details = request.json
    app.config['nodes_details'] = all_details
    wallet_public_key, ip_address, port = app.config['nodes_details'][0]
    node.wallet.update_utxo(wallet_public_key, [],
     [(0, 0, wallet_public_key, 100 * no_nodes)]) #sender, transaction_input, transaction_output)
    return jsonify({'status': 'success'})


def send_details_to_nodes(rest_nodes_details, node_id, cur_node_details,  responses):
    wallet_public_key, ip_address, port = cur_node_details
    node_url = 'http://' + ip_address + ":" + port

    response = requests.post(node_url + '/receive-network', json=rest_nodes_details)
    responses.append((response.json(), node_url))


def initial_transaction():

    for cur_key, cur_values in app.config['nodes_details'].items():
        if cur_key >0:
            wallet_public_key = cur_values[0]
            node.create_transaction(wallet_public_key, 100)


def broadcast_nodes_details():
    threads = []
    responses = []

    for cur_key, cur_values in app.config['nodes_details'].items():
        if cur_key > 0:
            temp_dict = {key: value for key, value in app.config['nodes_details'].items() if key != cur_key}
            thread = threading.Thread(target=send_details_to_nodes, args=(temp_dict, cur_key, cur_values, responses))
            threads.append(thread)
            thread.start()


    for thread in threads:
        thread.join()

    for resp, node_i in responses:
        if resp.status_code != 200:
            return 'Error sending information to some nodes.'
    return 'Information sent to all nodes successfully.'


def complete_network():
    broadcast_nodes_details()
    initial_transaction()


def update_nodes_details(details):
    app.config['nodes_details'][details['id']] = (details['wallet_public_key'], details['ip_address'], details['port'])


@app.route('/receive-details', method=['POST'])
def receive_details():
    details = request.json
    print("Node details:", details)
    update_nodes_details(details)

    app.config['node_counter'] += 1
    if app.config['node_counter'] == details['no_nodes']:
        #broadcast_nodes_details()
        threading.Thread(target=complete_network).start()

        # edw prepei na proste9ei na ksekinsoume gia ola ta nodes ta transaction??
    return jsonify({'status': 'success'})


@app.route('/receive-transaction', method=['POST'])
def receive_transaction():
    transaction_details = request.json
    return node.validate_transaction(transaction_details)
    # return jsonify({'status': 'success'})




#node = Node()
#app.config['node'] = node
