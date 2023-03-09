from wallet import Wallet
import main
import Crypto
from flask_cors import CORS
from flask import jsonify
from Crypto import Random
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from wallet import *
import requests
import block
import threading

from transaction import *
from flask_cors import CORS
from flask import jsonify
from main import app
# app = Flask(__name__)
# CORS(app)

class Node:
    def __init__(self, ip_address, port, bootstrap_ip_address, bootstrap_port, no_nodes, blockchain_snapshot=None,
                 key_length=2048):

        self.ip_address = ip_address
        self.port = port
        self.no_nodes = no_nodes

        self.bootstrap_node_url = 'http://' + bootstrap_ip_address + ":" + bootstrap_port
        self.wallet = self.generate_wallet(key_length)

        # self.id = self.get_node_id()
        if ip_address == bootstrap_ip_address:
            self.NBC = 100*self.no_nodes
            self.id = 0
            self.transaction_id = 0
            self.wallet.add_UTXO(self.wallet.get_public_key(), self.transaction_id, self.NBC)
            #self.UTXO = [(self.transaction_id, self.wallet.get_public_key(), self.NBC)]
            print(self.id)
        else:
            self.NBC = 0
            #bootstrap_node_url = 'http://' + bootstrap_ip_address + ":" + bootstrap_port
            self.id,b,c = self.insert_into_network()


    ##set

    # if(self.id == 0):

    # self.chain
    # self.current_id_count
    # self.NBCs
    # self.wallet

    # slef.ring[]   #here we store information for every node, as its id, its address (ip:port) its public key and its balance

    # @staticmethod
    # @app.route('/node-id')
    # def get_node_id():
    # 	node_id = app.config['node_id'] #app.config.get('NEXT_NODE_ID', 0)
    # 	app.config['node_id'] = node_id + 1
    # 	return str(node_id)

    # def create_new_block(self):
    #     return

    def generate_keys(self, key_length):
        random_generator = Random.new().read
        key = RSA.generate(key_length, random_generator)
        private_key = key.export_key()
        public_key = key.publickey().export_key()

        return public_key, private_key

    def generate_wallet(self, key_length):
        public_key, private_key = self.generate_keys(key_length)
        return Wallet(public_key, private_key, self.ip_address, None)

    # create a wallet for this node, with a public key and a private key

    # create a wallet for this node, with a public key and a private key

    def get_id(self):
        response = requests.get(self.bootstrap_node_url + '/node-id')
        response_dict = response.json()  # response_dict = json.loads(response_json)
        print(response_dict['node_id'])
        return response_dict['node_id']


    def send_details(self, details):
        response = requests.post(self.bootstrap_node_url + '/receive-details', json=details)
        return jsonify(response.json())

    def insert_into_network(self):
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # thelei ilopoisi

        id = self.get_id()

        details = {'id': id,
                   'wallet_public_key': self.wallet.get_public_key(),
                   'ip_address': self.ip_address,
                   'port': self.port,
                   'no_nodes': self.no_nodes}

        self.send_details(details)

        return id

    # add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
    # botstrap node informs all other nodes and gives the request node an id and 100 NBCs

    def create_transaction_input(self, UTXOs, wallet_public_key, amount):
        amount_left = amount
        change = 0
        cur_node_UTXOs = UTXOs[wallet_public_key]
        transaction_input = []
        for tr_id, NBC in cur_node_UTXOs:
            amount_left -= NBC
            transaction_input.append((tr_id, NBC))
            if amount_left - NBC <= 0:
                change = NBC - amount_left
                break

        if amount_left > 0:
            return [], 0

        return transaction_input, change

    def create_transaction(self, receiver_address, signature, amount):
        # na doume pws tha dimiourgoume to transaction id kai pws 9a kanoume validation na min einai amnoun < balance
        # bootstrap_node_url = 'http://' + bootstrap_ip_address + ":" + bootstrap_port
        response = requests.get(self.bootstrap_node_url + '/transaction-id')
        response_dict = response.json()
        # response_dict = json.loads(response_json)
        print(response_dict['node_id'])
        transaction_id = response_dict['transaction_id']

        if self.wallet.balance() < amount:
            print("Node" + self.id + ": could not make transaction, not enough money!")
        else:
            transaction_input, change = self.create_transaction_input(self.wallet.get_UTXOs(), self.wallet.get_public_key(), amount)
            if len(transaction_input) == 0:
                print("Not enough money for the transaction!")
                return None

            print("Node with wallet public key:", receiver_address, "will receive ", amount, "NBC")
            print("Node with wallet public key:", self.wallet.get_public_key(), "will have ", change,
                  "NBC left in that transaction")

            if change != 0:
                transaction_output = [(transaction_id, receiver_address, amount),
                                            (transaction_id, self.wallet.get_public_key(), change)]
            else:
                transaction_output = [(transaction_id, receiver_address, amount)]

            current_trans = Transaction(self.wallet.get_public_key(), transaction_id, transaction_input, transaction_output, self.wallet.get_private_key(), receiver_address, amount)
            # enhmerwtiko mhnyma !!!!!!!!!
            if self.broadcast_transaction(current_trans.to_dict()):
                print("Validate transaction make new UTXOS for that transaction")
            else:
                print("Not validate transaction!1!!")

    # remember to broadcast it

    def send_transaction(self, node_url, trans_dict):
        response = requests.post(node_url + '/receive-transaction', json=trans_dict)
        return jsonify(response.json())

    def broadcast_transaction(self, trans_dict):
        # edw prepei na kalestei i register_node_to_ring gia na mas ferie to daxtulidi apo publics key gia na lavoun olo
        # edw prepei na kalestei i register_node_to_ring gia na mas ferie to daxtulidi apo publics key gia na lavoun oli
        # edw prepei na kalestei i register_node_to_ring gia na mas ferie to daxtulidi apo publics key gia na lavoun ooi
        # edw prepei na kalestei i register_node_to_ring gia na mas ferie to daxtulidi apo publics key gia na lavoun loi
        # edw prepei na kalestei i register_node_to_ring gia na mas ferie to daxtulidi apo publics key gia na lavounoloi
        # edw prepei na kalestei i register_node_to_ring gia na mas ferie to daxtulidi apo publics key gia na lavou oloi
        # to transacrion

        threads = []
        responses = []
        network = app.config['nodes_details']
        for key, values in network:
            wallet_public_key, ip_address, port = values
            node_url = 'http://' + ip_address + ":" + port
            thread = threading.Thread(target=self.send_transaction, args=(node_url, trans_dict))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
            #responses.append(thread.result)  #pali edw thelei na to doume, einai to idio me prin.Apo katw thelei loupa se ola ta responses
                                                #dhladh an oloi dexthkan to transaction

        for resp in responses:
            if not resp["approve"]:
                print("Not validate!! Node with public key" + trans_dict["public_key"] + " has problem!")
                return False

        return True

    def verify_signature(self, signature, sender_address, recipient_address, value):
        transaction_data = str(sender_address) + str(recipient_address) + str(value)
        transaction_hash = SHA256.new(transaction_data.encode())
        public_key = RSA.importKey(binascii.unhexlify(sender_address))
        verifier = PKCS1_v1_5.new(public_key)
        signature = binascii.unhexlify(signature)
        return verifier.verify(transaction_hash, signature)

    def validate_transaction(self, trans):
        #trans = request.get_json()
        validate_sign = self.verify_signature(trans["signature"], trans["sender_address"], trans["recipient_address"], trans["value"])
        if validate_sign:
            if set(trans["transaction_inputs"]).intersection(self.wallet.get_UTXOs()[trans["sender_address"]]) == set(trans["transaction_inputs"]):
                self.wallet.update_utxo(trans["sender_address"], trans["transaction_inputs"], trans["transaction_outputs"])
                print("Validate transaction!!!")
                response = jsonify({"public_key": self.wallet.get_public_key(), "approve": True})
            else:
                print("Not validate amount for the transaction!!Scammer find!")
                response = jsonify({"public_key": self.wallet.get_public_key(), "approve": False})
        else:
            print("Not validate sign on the transaction!!Scammer find!")
            response = jsonify({"public_key": self.wallet.get_public_key(), "approve":  False})
        return response

#     def add_transaction_to_block():
#
#     # if enough transactions  mine
#
#     def mine_block():
#
#     def broadcast_block():
#
#     def valid_proof(.., difficulty=MINING_DIFFICULTY):
#
#     # concencus functions
#
#     def valid_chain(self, chain):
#
#     # check for the longer chain accroose all nodes
#
#     def resolve_conflicts(self):
# # resolve correct chain
