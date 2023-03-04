import block
from wallet import Wallet
from transaction import Transaction
import requests

class Node:
    def __init__(self, id, ip_address, port, blockchain_snapshot, key_length=2048):
        self.NBC = 100
        self.id = id
        self.ip_address = ip_address
        self.port = port

        self.wallet = self.generate_wallet(key_length)
        ##set

        if (self.id == 0):

    # self.chain
    # self.current_id_count
    # self.NBCs
    # self.wallet

    # slef.ring[]   #here we store information for every node, as its id, its address (ip:port) its public key and its balance

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

    def register_node_to_ring():

    # add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
    # bottstrap node informs all other nodes and gives the request node an id and 100 NBCs

    def create_transaction(self, receiver, signature, amount):
        # na doume pws tha dimiourgoume to transaction id kai pws 9a kanoume validation na min einai amnoun < balance
        transaction_id = 0
        current_trans = Transaction(self.wallet.get_address, transaction_id, self.wallet.get_transactions(),  self.wallet.get_private_key(), receiver, amount)
        self.broadcast_transaction(current_trans.transaction_outputs)

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



