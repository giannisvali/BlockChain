from wallet import Wallet
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
import base64
import binascii
from transaction import *
from flask_cors import CORS
from flask import jsonify


class Node:
    def __init__(self, ip_address, port, bootstrap_ip_address, bootstrap_port, no_nodes, blockchain_snapshot=None,
                 key_length=2048):

        self.ip_address = ip_address
        self.port = port
        self.no_nodes = no_nodes
        print(self.no_nodes)
        print(self.port)
        self.network = dict()

        self.bootstrap_node_url = 'http://' + bootstrap_ip_address + ":" + bootstrap_port
        self.wallet = self.generate_wallet(key_length)

        # self.id = self.get_node_id()
        if ip_address == bootstrap_ip_address:
            print("eimai o bootstrap kai eishltha")
            self.NBC = 100 * self.no_nodes
            self.id = 0
            self.transaction_id = 0
            # self.wallet.add_UTXO(self.wallet.get_public_key(), self.transaction_id, self.NBC)
            # #self.UTXO = [(self.transaction_id, self.wallet.get_public_key(), self.NBC)]
            self.wallet.update_utxo(self.wallet.get_public_key(), [],
                                    [(0, 0, self.wallet.get_public_key(), 100 * no_nodes)])

            print(self.id)
            self.network[self.id] = (self.wallet.get_public_key(), self.ip_address, self.port)
            # self.id = self.insert_into_network()

        else:
            self.NBC = 0
            # bootstrap_node_url = 'http://' + bootstrap_ip_address + ":" + bootstrap_port
            self.id = self.insert_into_network()

    def set_network(self, dict_net):
        self.network = dict_net
        print("Network:", self.network)

    @staticmethod
    def generate_keys(key_length):
        random_generator = Random.new().read
        key = RSA.generate(key_length, random_generator)
        # private_key = key.export_key()
        # public_key = key.publickey().export_key()
        private_key = binascii.hexlify(key.export_key()).decode('utf-8')
        public_key = binascii.hexlify(key.publickey().export_key()).decode('utf-8')

        return public_key, private_key

    def generate_wallet(self, key_length):
        public_key, private_key = self.generate_keys(key_length)
        return Wallet(public_key, private_key, self.ip_address, None)

    # create a wallet for this node, with a public key and a private key

    # create a wallet for this node, with a public key and a private key
    @staticmethod
    def check_status_code(response_status_code, expected_status_code = 200):
        if response_status_code!=expected_status_code:
            exit("Something went wrong when trying to connect to the network! Exiting...")

    def get_id(self):


        print(self.bootstrap_node_url + '/node-id')
        response = requests.get(self.bootstrap_node_url + '/node-id')
        print("eimai o slave", response.json(), flush = True)
        print(response.status_code)
        self.check_status_code(response.status_code, 200)
        data = response.json()

        #data = json.loads(response.content) #isodynamo me to response.json()
        #print(data)
        return data['node_id']
        #return response_dict['node_id']

    def send_details(self, details):
        print("stelnw ta details")
        response = requests.post(self.bootstrap_node_url + '/receive-details', json = details)#json=json.dumps(details).encode('utf-8'))
        print(response, flush = True)
        print(response.status_code)
        self.check_status_code(response.status_code, 200)
        return response #jsonify(response.json())

    def insert_into_network(self):
        id = self.get_id()
        print(type(id))
        print("loooool", id, flush=True)

        print(self.no_nodes)

        details = {'id': id,
                   #'wallet_public_key': self.wallet.get_public_key().decode('utf-8'),
                   'wallet_public_key': self.wallet.get_public_key(),
                   'ip_address': self.ip_address,
                   'port': self.port,
                   'no_nodes': self.no_nodes}

        self.send_details(details)

        return id

    # add this node to the ring, only the bootstrap node can add a node to the ring after checking
    # his wallet and ip:port address
    # botstrap node informs all other nodes and gives the request node an id and 100 NBCs

    def create_transaction_input(self, UTXOs, wallet_public_key, amount):
        # elegxoi: ama den yparxei to wallet_public_key kai ama to amount einai <=0 (kapou prepei na ginoun aytoi)
        amount_left = amount
        change = 0
        cur_node_UTXOs = UTXOs[wallet_public_key]
        transaction_input = []
        for tr_id, NBC in cur_node_UTXOs:
            transaction_input.append((tr_id, NBC))

            if amount_left - NBC <= 0:
                change = NBC - amount_left
                return transaction_input, change
            amount_left -= NBC


        if amount_left > 0:
            return [], 0


    def create_transaction(self, receiver_address, amount):  # yphrxe kai ena signature isws xreiastei\!!!!
        # na doume pws tha dimiourgoume to transaction id kai pws 9a kanoume validation na min einai amnoun < balance
        # bootstrap_node_url = 'http://' + bootstrap_ip_address + ":" + bootstrap_port
        response = requests.get(self.bootstrap_node_url + '/transaction-id')
        response_dict = response.json()
        print("UTXOS KATA TO CREATION TREANSACTIONl", self.wallet.get_UTXOs())
        # response_dict = json.loads(response_json)
        print(response_dict['transaction_id'])
        # ama parw transaction_id kai telika den ginei validate to transaction prepei na meiwsw to transaction_id kata 1
        transaction_id = response_dict['transaction_id']

        # if self.wallet.balance() < amount:
        #     print("Node" + self.id + ": could not make transaction, not enough money!")
        # else:
        transaction_input, change = self.create_transaction_input(self.wallet.get_UTXOs(),
                                                                  self.wallet.get_public_key(), amount)

        if len(transaction_input) == 0:
            print("Not enough money for the transaction!")
            return None

        print("Node with wallet public key:", receiver_address, "will receive ", amount, "NBC")
        print("Node with wallet public key:", self.wallet.get_public_key(), "will have ", change,
              "NBC left in that transaction")

        response = requests.get(self.bootstrap_node_url + '/transaction-output-id')
        response_dict = response.json()
        print(response_dict['transaction_output_id'])
        # ama parw transaction_id kai telika den ginei validate to transaction prepei na meiwsw to transaction_id kata 1

        transaction_output_id1 = response_dict['transaction_output_id']
        if change != 0:
            response = requests.get(self.bootstrap_node_url + '/transaction-output-id')
            response_dict = response.json()
            print(response_dict['transaction_output_id'])
            # ama parw transaction_id kai telika den ginei validate to transaction prepei na meiwsw to transaction_id kata 1

            transaction_output_id2 = response_dict['transaction_output_id']
            transaction_output = [(transaction_output_id1, transaction_id, receiver_address, amount),
                                  (transaction_output_id2, transaction_id, self.wallet.get_public_key(), change)]
        else:
            transaction_output = [(transaction_output_id1, transaction_id, receiver_address, amount)]



        current_trans = Transaction(self.wallet.get_public_key(), transaction_id, transaction_input,
                                    transaction_output, self.wallet.get_private_key(), receiver_address, amount)

        print("CURRENT TRANS:", current_trans.to_dict())

        # enhmerwtiko mhnyma !!!!!!!!!
        if self.broadcast_transaction(current_trans.to_dict()):
            print("Validate transaction make new UTXOS for that transaction")
            self.wallet.update_utxo(current_trans.sender_address, current_trans.transaction_inputs, current_trans.transaction_output)
        else:
            response = requests.get(self.bootstrap_node_url + '/reduce-transaction-output-id')
            response_dict = response.json()
            print(response_dict['transaction_output_id'])
            if change != 0:
                response = requests.get(self.bootstrap_node_url + '/reduce-transaction-output-id')
                response_dict = response.json()
                print(response_dict['transaction_output_id'])

            print("Not validate transaction!!")

    # remember to broadcast it

    def send_transaction(self, node_url, trans_dict, responses):
        print("stelnw send transaction")
        print(trans_dict)
        print(type(trans_dict))
        # trans_dict['sender_address'] = trans_dict['sender_address'].decode('utf-8')
        # trans_dict['recipient_address'] = trans_dict['recipient_address'].decode('utf-8')
        #trans_dict['signature'] = trans_dict['signature'].decode('utf-8')

        response = requests.post(node_url + '/receive-transaction', json = trans_dict)
        print("send transaction response:", response, flush  = True)
        responses.append((response.json(), node_url))

    def broadcast_transaction(self, trans_dict):
        threads = []
        responses = []
        # network = main.app.config['nodes_details']
        for key, values in self.network.items():
            wallet_public_key, ip_address, port = values
            print(ip_address, port)
            node_url = 'http://' + ip_address + ":" + port
            thread = threading.Thread(target=self.send_transaction, args=(node_url, trans_dict, responses))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
            # responses.append(thread.result)  #pali edw thelei na to doume,
            # einai to idio me prin.Apo katw thelei loupa se ola ta responses
            # dhladh an oloi dexthkan to transaction

        for resp, node in responses:
            if not resp["approve"]:
                print("Not validate!! Node with public key" + trans_dict["public_key"] + " has problem!" + node)
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
        # trans = request.get_json()
        print("validate_transaction:", type(trans))
        validate_sign = self.verify_signature(trans["signature"], trans["sender_address"], trans["recipient_address"],
                                              trans["value"])
        print("validate sign")

        if validate_sign:
            #baraei epeidh mia lista de mporei na mpei mesa se ena set
            trans["transaction_inputs"] = [tuple(inner_list) for inner_list in trans["transaction_inputs"]]
            if set(trans["transaction_inputs"]).intersection(self.wallet.get_UTXOs()[trans["sender_address"]]) == set(
                    trans["transaction_inputs"]):
                self.wallet.update_utxo(trans["sender_address"], trans["transaction_inputs"],
                                        trans["transaction_outputs"])
                print("Validate transaction v4!!!")
                response = jsonify({"public_key": self.wallet.get_public_key(), "approve": True})
            else:
                print("Not validate amount for the transaction!!Scammer find!")
                response = jsonify({"public_key": self.wallet.get_public_key(), "approve": False})
        else:
            print("Not validate sign on the transaction!!Scammer find!")
            response = jsonify({"public_key": self.wallet.get_public_key(), "approve": False})
        return response

#     def add_transaction_to_block():
#
#     # if enough transactions  mine
#
# def mine_block(self):
#     mined_block = self.blockchain.get_mined_block()
#     # check if chain's last block remains the same - maybe block added by another node
#     if mined_block.previousHash == self.blockchain.get_last_block_hash():
#         self.blockchain.add_block_to_chain(mined_block)
#         # self.broadcast_block(mined_block)
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
