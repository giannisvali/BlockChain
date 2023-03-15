import requests
from flask import Flask, request
from argparse import ArgumentParser
from node import *
# from importlib import reload
# reload(node)
from flask_cors import CORS
from flask import jsonify, Response
import threading
import base64
#aaaaaaaaaa
app = Flask(__name__)
CORS(app)
app.config['node_id'] = 1
app.config['transaction_id'] = 1
app.config['nodes_details'] = dict()
app.config['node_counter'] = 1
app.config['transaction_output_id'] = 1



# def positive_int(value):
#     ivalue = int(value)
#     if ivalue <= 0:
#         raise argparse.ArgumentTypeError("%s is not a positive integer" % value)
#     return ivalue


@app.route('/node-id')
def get_node_id():

    node_id = app.config.get('node_id', 0)
    app.config['node_id'] = node_id + 1
    response = jsonify({"node_id": node_id})
    return response, 200


@app.route('/transaction-id')
def get_transaction_id():
    transaction_id = app.config['transaction_id']  # app.config.get('NEXT_NODE_ID', 0)
    app.config['transaction_id'] = transaction_id + 1
    response = jsonify({"transaction_id": transaction_id})
    return response

@app.route('/transaction-output-id')
def get_transaction_output_id():
    transaction_output_id = app.config['transaction_output_id']  # app.config.get('NEXT_NODE_ID', 0)
    app.config['transaction_output_id'] = transaction_output_id + 1
    response = jsonify({"transaction_output_id": transaction_output_id})
    return response


@app.route('/reduce-transaction-output-id')
def reduce_transaction_output_id():
    app.config['transaction_output_id']-=1
    return jsonify({'status': 'success'})


@app.route('/receive-network', methods=['POST'])
def receive_network():
    all_details = request.json
    app.config['nodes_details'] = all_details
    cur_node.set_network(app.config['nodes_details'])
    print("APP CONFIG:", app.config['nodes_details'])
    wallet_public_key, ip_address, port = app.config['nodes_details']['0']  #bootstrap node details
    cur_node.wallet.update_utxo(wallet_public_key, [],
     [(0, 0, wallet_public_key, 100 * no_nodes)]) #sender, transaction_input, transaction_output)
    return jsonify({'status': 'success'})


@app.route('/receive-block', methods=['POST'])
def receive_block():
    block_dict = request.json
    # create block object from dictionary received
    block = Block(index=block_dict['index'], timestamp=block_dict['timestamp'], transactions=block_dict['transactions'],
                  nonce=block_dict['nonce'], previousHash=block_dict['previous_hash'], hash=block_dict['hash'])
    # if mined block previous hash = node's last block's hash and hash of mined block is valid --> add block else reject
    # if mined block previous hash != node's last block's hash : node received block from other miner - 2nd block
    # if mined block is valid but its previous hash is not contained in chain: conflict, not 2nd block from 2nd miner
    if block.previousHash == cur_node.blockchain.get_last_block_hash():
        if cur_node.validate_block(block):
            cur_node.blockchain.add_block(block)
            response = jsonify({'message': 'Node {} added block to blockchain'.format(cur_node.id)})
            return response, 200
        else:
            response = {'message': 'Block rejected from {} - hash is not valid'.format(cur_node.id)}
            return jsonify(response), 400
        #periptwsi conflict: ean to previous hash tou block den uparxei sthn alysida
        #etsi diaxwrizetai apo thn periptwsi tis deuterhs afiksis block apo ton tautoxrono miner
    elif cur_node.validate_block(block) and not(cur_node.blockchain.hash_exists_in_chain(block.previous_hash)):
        #TODO: Thread needed?, asks for chain every node, mporei kai oxi
        cur_node.resolve_conflict()
        response = {'message': 'Resolving Conflict'}
        return jsonify(response), 200
    else:
        response = jsonify({'message': 'Block rejected from {} - previous hash not the same - second block received from simultaneous miner'.format(cur_node.id)})
        return response, 400


def send_details_to_nodes(rest_nodes_details, node_id, cur_node_details,  responses):
    wallet_public_key, ip_address, port = cur_node_details
    node_url = 'http://' + ip_address + ":" + port

    response = requests.post(node_url + '/receive-network', json=rest_nodes_details)
    #responses.append((response.json(), node_url))
    responses.append((response, cur_node_details))

def broadcast_nodes_details():
    threads = []
    responses = []

    for cur_key, cur_values in app.config['nodes_details'].items():
        print("CUR KEYYY", cur_key)
        if str(cur_key) != '0':
            temp_dict = {key: value for key, value in app.config['nodes_details'].items()}
            thread = threading.Thread(target=send_details_to_nodes, args=(temp_dict, cur_key, cur_values, responses))
            threads.append(thread)
            thread.start()


    for thread in threads:
        thread.join()


    for resp, node_i in responses:
        if resp.status_code != 200: #edw isws baloume se poio node yphrxe problhma xrhsimopoiwntas ta stoixeia tou node_i = (wallet_public_key, ip_address, port)
            return 'Error sending information to some nodes.'
    return 'Information sent to all nodes successfully.'


def initial_transaction():

    for cur_key, cur_values in app.config['nodes_details'].items():
        #if str(cur_key) != '0':
        if str(cur_key) != '0':
            print("eimai sto initial transaction")
            wallet_public_key = cur_values[0]
            cur_node.create_transaction(wallet_public_key, 100)

    print("teleiwsa ta initial transactions")

def complete_network():
    print("complete1")
    cur_node.set_network(app.config['nodes_details'])
    print("complete2")

    broadcast_nodes_details()
    print("complete3")

    initial_transaction()
    print("complete4")

    print("Node UTXO!!!", cur_node.wallet.get_UTXOs())



def update_nodes_details(details):

    #app.config['nodes_details'][details['id']] = (details['wallet_public_key'].encode('utf-8'), details['ip_address'], details['port'])
    app.config['nodes_details'][str(details['id'])] = (details['wallet_public_key'], details['ip_address'], details['port'])
    #base64.b64decode

@app.route('/receive-details', methods=['POST'])
def receive_details():
    print("mphka sto receive details", flush = True)
    data = request.get_data()
    details = json.loads(data)
    # details = request.get_json()
    # print(type(details))
    update_nodes_details(details)

    app.config['node_counter'] += 1
    if app.config['node_counter'] == cur_node.no_nodes:#details['no_nodes']:
        print("mazeythkame oloi!")
        bootstrap_details = {'id': cur_node.id,
                   #'wallet_public_key': cur_node.wallet.get_public_key().decode('utf-8'),
                   'wallet_public_key': cur_node.wallet.get_public_key(),
                   'ip_address': cur_node.ip_address,
                   'port': cur_node.port,
                   'no_nodes': cur_node.no_nodes}

        update_nodes_details(bootstrap_details)
        print("APP CONFIG AFTER BOOTSTRAP:", app.config["nodes_details"])

        #broadcast_nodes_details()
        threading.Thread(target=complete_network).start()

        # edw prepei na proste9ei na ksekinsoume gia ola ta nodes ta transaction??
    return jsonify({'status': 'success'})


@app.route('/receive-transaction', methods=['POST'])
def receive_transaction():
    # data = request.get_data()
    # details = json.loads(data)
    # print("transaction details:", details, flush = True)
    transaction_details = request.json
    print("transaction details:", transaction_details, flush = True)
    # transaction_details['sender_address'] = transaction_details['sender_address'].encode('utf-8')
    # transaction_details['recipient_address'] = transaction_details['recipient_address'].decode('utf-8')
    #transaction_details['signature'] = transaction_details['signature'].decode('utf-8')

    return cur_node.validate_transaction(transaction_details)
    # return jsonify({'status': 'success'})



if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--ip', default='127.0.0.1', type=str)
    parser.add_argument('--port', default='5000', type=str)
    parser.add_argument('--bootstrap_ip', default='127.0.0.1', type=str)
    parser.add_argument('--bootstrap_port', default='5000', type=str)
    parser.add_argument('--is_bootstrap', type=int, choices=[0, 1], default=0)
    # parser.add_argument('--capacity', default=5000, type=positive_int)
    parser.add_argument('--capacity', default=4, type=int)
    parser.add_argument('--difficulty', default=3, type=int)
    parser.add_argument('--no_nodes', default=3, type=int)
    parser.add_argument('--app_port', default=5000, type = int)

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
    app_port = args.app_port
    print(no_nodes)

    global cur_node
    cur_node = Node(ip_address, port, bootstrap_ip_address, bootstrap_port, no_nodes, capacity, difficulty, blockchain_snapshot=None,
                key_length=2048)
    app.run(host='0.0.0.0', port=app_port)#, debug=True)




#node = Node()
#app.config['node'] = node
