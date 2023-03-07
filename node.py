from wallet import Wallet
import main
import Crypto
from Crypto import Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from wallet import *
import requests
import block
from transaction import *
class Node:
    def __init__(self, ip_address, port, bootstrap_ip_address, bootstrap_port, no_nodes, blockchain_snapshot=None,
                 key_length=2048):

        self.ip_address = ip_address
        self.port = port
        self.bootstrap_node_url = 'http://' + bootstrap_ip_address + ":" + bootstrap_port
        self.wallet = self.generate_wallet(key_length)

        # self.id = self.get_node_id()
        if ip_address == bootstrap_ip_address:
            self.NBC = 100*no_nodes
            self.id = 0
            self.transaction_id = 0
            self.wallet.add_UTXO(self.wallet.get_public_key(), self.transaction_id, self.NBC)
            #self.UTXO = [(self.transaction_id, self.wallet.get_public_key(), self.NBC)]
            print(self.id)
        else:
            self.NBC = 0
            #bootstrap_node_url = 'http://' + bootstrap_ip_address + ":" + bootstrap_port
            response = requests.get(self.bootstrap_node_url + '/node-id')
            response_dict = response.json()
            # response_dict = json.loads(response_json)
            print(response_dict['node_id'])
            self.id = response_dict['node_id']



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
        return Wallet(public_key, private_key, self.ip_address, None)

    # create a wallet for this node, with a public key and a private key

    # create a wallet for this node, with a public key and a private key

    def register_node_to_ring(self):
        pass
    # add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
    # bottstrap node informs all other nodes and gives the request node an id and 100 NBCs

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

        #bootstrap_node_url = 'http://' + bootstrap_ip_address + ":" + bootstrap_port
        response = requests.get(self.bootstrap_node_url + '/transaction-id')
        response_dict = response.json()
        # response_dict = json.loads(response_json)
        print(response_dict['node_id'])
        transaction_id = response_dict['transaction_id']

        if self.wallet.balance()<amount:
            print("Node" + self.id + ": could not make transaction, not enough money! xypna mlk")
        else:
            transaction_input, change  = self.create_transaction_input(self.wallet.get_UTXOs(), self.wallet.get_public_key(), amount)
            if len(transaction_input)==0:
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
            #enhmerwtiko mhnyma !!!!!!!!!
            self.broadcast_transaction(current_trans.transaction_output )

    # remember to broadcast it


    def broadcast_transaction(self, message):

    def validate_transaction():

    # use of signature and NBCs balance

    def add_transaction_to_block():

    # if enough transactions  mine

    def mine_block():

    def broadcast_block():

    def valid_proof(.., difficulty=MINING_DIFFICULTY):

    # concencus functions

    def valid_chain(self, chain):

    # check for the longer chain accroose all nodes

    def resolve_conflicts(self):
# resolve correct chain
