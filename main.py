import requests
from flask import Flask, request
from argparse import ArgumentParser
from node import *
# from importlib import reload
# reload(node)
from flask_cors import CORS
from flask import jsonify, Response
import threading
import jsonpickle
import base64
import time
import datetime
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



@app.route('/specific-node')
def get_specific_node():
    data = request.json
    node_id = data['node_id']
    if node_id not in app.config['nodes_details']:
        return jsonify({"node_details": None}), 404

    return jsonify({"node_details": app.config['nodes_details'][node_id]}), 200


@app.route('/find-wallet-public-key')
def find_wallet_public_key():
    details = request.json
    wallet_public_key = details['wallet_public_key']
    print(wallet_public_key)
    for cur_key, cur_values in app.config['nodes_details'].items():
        if cur_values[0] == wallet_public_key:
            return jsonify({"details": app.config['nodes_details'][cur_key]}), 200


    return jsonify({"response": None}), 404



@app.route('/create-client-transaction', methods=['POST'])
def create_client_transaction():
    details = request.json
    wallet_public_key = details['wallet_public_key'] #get public key of receiver
    NBC = details['NBC']
    valid_transaction = cur_node.create_transaction(wallet_public_key, int(NBC))

    if not valid_transaction:
        return jsonify({"response": None}), 403
    return jsonify({"response": None}), 201

    # if node_id not in app.config['nodes_details']:
    #     return jsonify({"node_details": None}), 404
    #
    # return jsonify({"node_details": app.config['nodes_details'][node_id]}), 200


@app.route('/last-block-transactions')
def last_block_transactions():

    return jsonify({"transactions": cur_node.blockchain.get_last_block().listOfTransactions}), 200


@app.route('/balance')
def get_balance():
    return jsonify({"balance": cur_node.wallet.balance()}), 200


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



@app.route('/receive-block', methods=['POST'])
def receive_block():
    print('------------------------- BLOCK RECEIVED -------------------------------------------------------------\n')
    block_data = request.get_json(force = True)
    block_dict = dict(jsonpickle.decode(block_data))
    # create block object from dictionary received
    # print('\n \n RECEIVED BLOCK TRANSACTIONS {} \n \n', block_dict['transactions'])
    block = Block(index=block_dict['index'], timestamp=block_dict['timestamp'], transactions=block_dict['transactions'],
                  nonce=block_dict['nonce'], previousHash=block_dict['previous_hash'], hash=block_dict['hash'])
    # if mined block previous hash = node's last block's hash and hash of mined block is valid --> add block else reject
    # if mined block previous hash != node's last block's hash : node received block from other miner - 2nd block
    # if mined block is valid but its previous hash is not contained in chain: conflict, not 2nd block from 2nd miner
    if block.previousHash == cur_node.blockchain.get_last_block_hash():
        cur_chain_length = len(cur_node.blockchain.chain)
        if cur_node.validate_block(block):
            cur_node.blockchain.add_block(block)
            response = jsonify({'message': 'Node {} added block to blockchain'.format(cur_node.id)})
            #print('BLOCK REJECTED BECAUSE HASH IS NOT VALID')
            return response, 200
        else:
            if cur_chain_length < len(cur_node.blockchain.chain):
                response = {'message': 'mining (->node added its block and will reject the incoming) finished while in validate block'.format(cur_node.id)}
                return jsonify(response), 400
            else:
                response = {'message': 'Block rejected from {} - hash is not valid '.format(cur_node.id)}
                return jsonify(response), 400
        #periptwsi conflict: ean to previous hash tou block den uparxei sthn alysida
        #etsi diaxwrizetai apo thn periptwsi tis deuterhs afiksis block apo ton tautoxrono miner
    elif not(cur_node.blockchain.hash_exists_in_chain(block.previousHash)) and cur_node.validate_block(block):
        #TODO: Thread needed?, asks for chain every node, mporei kai oxi
        cur_node.resolve_conflict()
        response = {'message': 'Resolving Conflict'}
        return jsonify(response), 200
    else:
        print('BLOCK REJECTED BECAUSE PREVIOUS HASH IS NOT THE SAME - MULTIPLE ARRIVALS')
        response = jsonify({'message': 'Block rejected from {} - previous hash not the same - second block received from simultaneous miner'.format(cur_node.id)})
        return response, 400

@app.route('/chain', methods=['GET'])
def give_chain():
    print('-----------------------------------GIVE CHAIN---------------------------------------------')
    response = jsonpickle.encode(cur_node.blockchain.chain, unpicklable=True)
    return jsonify(response), 200


@app.route('/receive-network', methods=['POST'])
def receive_network():
    print("kanw receive to network", flush = True)
    data = request.json
    app.config['nodes_details'] = data['details']
    cur_node.set_network(app.config['nodes_details'])
    print("APP CONFIG:", app.config['nodes_details'])


    cur_node.wallet.set_utxo(data['UTXOs'])
    chain = jsonpickle.decode(data['chain'])
    if cur_node.validate_chain(chain):
        cur_node.blockchain.set_chain(chain)

    cur_node.blockchain.set_unmined_transactions(data['unmined_transactions'])


    # wallet_public_key, ip_address, port = app.config['nodes_details']['0']  #bootstrap node details
    #
    # cur_node.wallet.update_utxo(wallet_public_key, [],
    #  [(0, 0, wallet_public_key, 100 * no_nodes)]) #sender, transaction_input, transaction_output)
    #
    #
    # print("RECEIVE NETWORK GET UTXOS", flush = True)
    # print(cur_node.wallet.get_UTXOs(),flush = True)

    return jsonify({'status': 'success'})




def send_details_to_node(rest_nodes_details, cur_node_details):
    wallet_public_key, ip_address, port = cur_node_details
    print(ip_address, port)
    temp_node_url = "http://" + ip_address + ":" + port
    print("send_details_to_node", temp_node_url)
    time.sleep(0.01)
    response = requests.post(temp_node_url + '/receive-network', json=rest_nodes_details)

    #responses.append((response.json(), node_url))
    return response

@app.route('/update-network', methods=['POST'])
def update_network():
    print("kanw update to network")
    data = request.json

    app.config['nodes_details'][str(data["details"]['id'])] = (data["details"]['wallet_public_key'], data["details"]['ip_address'], data["details"]['port'])
    cur_node.set_network(app.config['nodes_details'])
    return jsonify({'status': 'success'})

def send_details_to_nodes(rest_nodes_details, cur_node_id, cur_node_details, new_node_details, UTXOs, chain, unmined_transactions, responses):
    time.sleep(0.01)
    #args=(temp_dict, cur_key, cur_values, new_node_details, UTXOs, chain, unmined_transactions, responses))

    if str(cur_node_id) == str(new_node_details['id']):
        #time.sleep(1)
        temp_node_url = "http://" + new_node_details['ip_address'] + ":" + new_node_details['port']
        print("send_details_to_node", temp_node_url)

        data = {"details": rest_nodes_details, "UTXOs": UTXOs, "chain": jsonpickle.encode(chain, unpicklable=True), "unmined_transactions": unmined_transactions}
        response = requests.post(temp_node_url + '/receive-network', json=data)
        #responses.append((response.json(), node_url))
        responses.append((response, cur_node_details))
    else:

        wallet_public_key, ip_address, port = cur_node_details
        print(ip_address, port)
        temp_node_url = "http://" + ip_address + ":" + port
        print("send_details_to_node", temp_node_url)

        data = {"details": new_node_details}

        response = requests.post(temp_node_url + '/update-network', json=data)
        # responses.append((response.json(), node_url))
        responses.append((response, cur_node_details))


def broadcast_nodes_details(UTXOs, chain, unmined_transactions, new_node_details):
    threads = []
    responses = []

    for cur_key, cur_values in app.config['nodes_details'].items():
        if str(cur_key) != '0':
            print("CUR KEYYY", cur_key, cur_values)
            temp_dict = {key: value for key, value in app.config['nodes_details'].items()}
            thread = threading.Thread(target=send_details_to_nodes, args=(temp_dict, cur_key, cur_values, new_node_details, UTXOs, chain, unmined_transactions, responses))
            threads.append(thread)
            thread.start()


    for thread in threads:
        thread.join()


    for resp, node_i in responses:
        if resp.status_code != 200: #edw isws baloume se poio node yphrxe problhma xrhsimopoiwntas ta stoixeia tou node_i = (wallet_public_key, ip_address, port)
            return 'Error sending information to some nodes.'
    return 'Information sent to all nodes successfully.'


def initial_transaction(wallet_public_key):

    print("wallet public key:", wallet_public_key)
    cur_node.create_transaction(wallet_public_key, 100)

    print("teleiwsa ta initial transactions")


@app.route('/receive-transactions-request', methods=['POST'])
def receive_transactions_request():
    print("kanw receive to transaction request")
    data = request.json
    processed_transactions = cur_node.execute_file_transactions(data['filepath'])

    return jsonify({'status': 'success', 'processed_transactions': processed_transactions})


def send_transactions_request(node_id, cur_node_details, filepath, responses):
    wallet_public_key, ip_address, port = cur_node_details
    print(ip_address, port)
    temp_node_url = "http://" + ip_address + ":" + port
    print("send transaction request to node", temp_node_url)
    data = {"filepath": filepath}
    response = requests.post(temp_node_url + '/receive-transactions-request', json=data)
    responses.append((response, cur_node_details)) #ama theloume na printaroume mhnymata isws na baloume to node_id anti gia to cur_node_details


@app.route('/calculate-block-time', methods=['GET'])
def calculate_block_time():
    print("kanw receive to transaction request")
    block_timestamps = cur_node.blockchain.block_timestamps
    data = request.json

    block_timestamps.insert(0, datetime.datetime.strptime(data['start_block_timestamp'], '%Y-%m-%dT%H:%M:%S.%f'))#.fromisoformat())
    timestamp_differences = []
    for i in range(len(block_timestamps) - 1):
        diff = block_timestamps[i + 1] - block_timestamps[i]  #calculate time difference
        timestamp_differences.append(diff.total_seconds())  #add difference to list

    avg_diff = sum(timestamp_differences) / len(timestamp_differences)  #calculate average difference
    print(f"Average time difference: {avg_diff:.4f} seconds")
    return jsonify({'status': 'success', 'block_time': avg_diff})


def block_time(node_id, cur_node_details, start_block_timestamp, responses):
    wallet_public_key, ip_address, port = cur_node_details
    temp_node_url = "http://" + ip_address + ":" + port
    data = {"start_block_timestamp": start_block_timestamp.isoformat()}
    response = requests.get(temp_node_url + '/calculate-block-time', json=data)
    responses.append((response, cur_node_details))

def begin_transactions():
    threads = []
    responses = []
    path_base = "./" + str(cur_node.no_nodes) + "nodes/"
    path_base = "./" + "5" + "nodes/" #na to diwxw auto metaaaa!~`!!
    start_time = time.perf_counter()
    start_block_timestamp = datetime.datetime.now()


    for cur_key, cur_values in app.config['nodes_details'].items():
        filepath = path_base + "transaction" + cur_key + ".txt"  #na to epistrepsw se "transactions" anti gia "transaction"
        thread = threading.Thread(target=send_transactions_request, args=(cur_key, cur_values, filepath, responses))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    elapsed_time = time.perf_counter() - start_time
    print("Elapsed time: {:.4f} seconds".format(elapsed_time))

    total_transactions = 0
    for resp, node_i in responses:
        if resp.status_code != 200:  # edw isws baloume se poio node yphrxe problhma xrhsimopoiwntas ta stoixeia tou node_i = (wallet_public_key, ip_address, port)
            return 'Error beginning transactions to some nodes.'

        total_transactions+=resp.json()['processed_transactions']

    print("Throughput: {:.4f} transactions per second".format(total_transactions/elapsed_time))



    threads = []
    responses = []
    for cur_key, cur_values in app.config['nodes_details'].items():
        thread = threading.Thread(target=block_time, args=(cur_key, cur_values, start_block_timestamp, responses))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    total_block_time = 0
    for resp, node_i in responses:
        if resp.status_code != 200:  # edw isws baloume se poio node yphrxe problhma xrhsimopoiwntas ta stoixeia tou node_i = (wallet_public_key, ip_address, port)
            return 'Error beginning transactions to some nodes.'

        total_block_time += resp.json()['block_time']


    #Block time for each node is calculated. To find the global block time we just have to take the average block time for all the nodes,

    print("Block time: {:.4f} seconds".format(total_block_time/len(responses)))

    with open('log_' + str(cur_node.no_nodes) + 'nodes.txt', 'w') as f:
        f.write("Elapsed time: {:.4f} seconds\n".format(elapsed_time))
        f.write("Throughput: {:.4f} transactions per second\n".format(total_transactions/elapsed_time))
        f.write("Block time: {:.4f} seconds\n".format(total_block_time/len(responses)))

    print('Transactions were executed to all nodes successfully.')





def complete_network(new_node_details):

    update_nodes_details(new_node_details)
    broadcast_nodes_details(cur_node.wallet.UTXOs, cur_node.blockchain.chain,
                            cur_node.blockchain.get_unmined_transactions(), new_node_details)

    initial_transaction(new_node_details['wallet_public_key'])

    app.config['node_counter'] += 1
    if app.config['node_counter'] == cur_node.no_nodes:
        print("mazeythkame oloi!")
        begin_transactions()



def update_nodes_details(details):

    app.config['nodes_details'][str(details['id'])] = (details['wallet_public_key'], details['ip_address'], details['port'])
    cur_node.set_network(app.config['nodes_details'])

@app.route('/receive-details', methods=['POST'])
def receive_details():
    print("mphka sto receive details", flush = True)
    data = request.get_data()
    new_node_details = json.loads(data)

    print(new_node_details)
    thread = threading.Thread(target=complete_network, args=([new_node_details]))
    thread.start()

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
    if ip_address == bootstrap_ip_address:
        bootstrap_details = {'id': cur_node.id,
                             # 'wallet_public_key': cur_node.wallet.get_public_key().decode('utf-8'),
                             'wallet_public_key': cur_node.wallet.get_public_key(),
                             'ip_address': cur_node.ip_address,
                             'port': cur_node.port,
                             'no_nodes': cur_node.no_nodes}

        update_nodes_details(bootstrap_details)
    app.run(host='0.0.0.0', port=app_port)#, debug=True)




#node = Node()
#app.config['node'] = node
