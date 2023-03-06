import block
import wallet
import main
from main import *
import Crypto
from Crypto import Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from wallet import *
import requests


class Node:
    def __init__(self, ip_address, port, bootstrap_ip_address, bootstrap_port, blockchain_snapshot=None,
                 key_length=2048):
        self.NBC = 100
        # self.id = self.get_node_id()
        if (ip_address == bootstrap_ip_address):
            self.id = 0
            print(self.id)
        else:
            bootstrap_node_url = 'http://' + bootstrap_ip_address + ":" + bootstrap_port
            response = requests.get(bootstrap_node_url + '/node-id')
            response_dict = response.json()
            # response_dict = json.loads(response_json)
            print(response_dict['node_id'])
            self.id = response_dict['node_id']

        self.ip_address = ip_address
        self.port = port

        self.wallet = self.generate_wallet(key_length)

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

    def create_new_block(self):
        return

    def generate_keys(self, key_length):
        random_generator = Random.new().read
        key = RSA.generate(key_length, random_generator)
        private_key = key.export_key()
        public_key = key.publickey().export_key()

        return public_key, private_key

    def generate_wallet(self, key_length):

        public_key, private_key = self.generate_keys(key_length)
        return Wallet(public_key, private_key, None, None)

    # create a wallet for this node, with a public key and a private key

# def register_node_to_ring():
# 	#add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
# 	#bottstrap node informs all other nodes and gives the request node an id and 100 NBCs
# 	pass
#
# def create_transaction(sender, receiver, signature):
# 	#remember to broadcast it
# 	pass
#
# def broadcast_transaction():
# 	pass
#
#
#
#
# def validdate_transaction():
# 	#use of signature and NBCs balance
# 	pass
#
# def add_transaction_to_block():
# 	#if enough transactions  mine
# 	pass
#
#
# def mine_block():
# 	pass
#
#
# def broadcast_block():
# 	pass
#
#
#
# def valid_proof(.., difficulty=MINING_DIFFICULTY):
# 	pass
#
#
#
# #concencus functions
#
# def valid_chain(self, chain):
# 	#check for the longer chain accroose all nodes
#
#
# def resolve_conflicts(self):
# 	#resolve correct chain
