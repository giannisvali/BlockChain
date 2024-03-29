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
from flask import jsonify
from blockchain import Blockchain
from block import Block
import jsonpickle
import time

class Node:

    def __init__(self, ip_address, port, bootstrap_ip_address, bootstrap_port, no_nodes, capacity, difficulty,
                 blockchain_snapshot=None,
                 key_length=2048):
        self.ip_address = ip_address
        self.port = port
        self.no_nodes = no_nodes
        self.network = dict()

        self.block_lock = threading.Lock()

        # TODO: pass capacity to blockchain
        self.blockchain = Blockchain(capacity=capacity, difficulty=difficulty)

        self.bootstrap_node_url = 'http://' + bootstrap_ip_address + ":" + bootstrap_port
        self.wallet = self.generate_wallet(key_length)
        # use flag to see when a block is under mining
        self.is_mining = False

        # self.id = self.get_node_id()
        if ip_address == bootstrap_ip_address and port == bootstrap_port:
            self.NBC = 100 * self.no_nodes
            self.id = 0
            self.transaction_id = 0
            # self.wallet.add_UTXO(self.wallet.get_public_key(), self.transaction_id, self.NBC)
            # #self.UTXO = [(self.transaction_id, self.wallet.get_public_key(), self.NBC)]
            self.wallet.update_utxo(self.wallet.get_public_key(), [],
                                    [(0, 0, self.wallet.get_public_key(), 100 * no_nodes)])

            trans = Transaction(transaction_id=0, sender_address= 0,#sender_address=self.wallet.get_public_key(),
                                recipient_address=self.wallet.get_public_key(),
                                transaction_input=[],
                                transaction_output=[(0, 0, self.wallet.get_public_key(), no_nodes * 100)],
                                sender_private_key=self.wallet.get_private_key(),
                                value=no_nodes * 100)



            self.blockchain.add_block(Block(previousHash=1, nonce=0, index=0, transactions=[trans.to_dict()]), timestamp=False)

            self.network[self.id] = (self.wallet.get_public_key(), self.ip_address, self.port)
            # self.id = self.insert_into_network()

        else:
            self.NBC = 0
            # bootstrap_node_url = 'http://' + bootstrap_ip_address + ":" + bootstrap_port
            self.id = self.insert_into_network()
            # response = requests.get(self.bootstrap_node_url + '/chain')
            # self.check_status_code(response.status_code, 200)
            # chain = jsonpickle.decode(response.json())

            # if self.validate_chain(chain):
            #     print('CHAIN IS VALID')
            #     print("Chain received from bootstrap has been validated.")

            # if self.validate_chain(chain):
            #     self.blockchain.chain = chain

            # chain = jsonpickle.decode(response.json())
            # if self.validate_chain(chain):
            #     print("Chain received from bootstrap has been validated.")
            #     self.blockchain.chain = chain





    def set_network(self, dict_net):
        self.network = dict_net

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
    def check_status_code(response_status_code, expected_status_code=200):
        if response_status_code != expected_status_code:
            exit("Something went wrong when trying to connect to the network! Exiting...")

    def get_id(self):

        response = requests.get(self.bootstrap_node_url + '/node-id')
        self.check_status_code(response.status_code, 200)
        data = response.json()


        return data['node_id']
        # return response_dict['node_id']

    def send_details(self, details):
        response = requests.post(self.bootstrap_node_url + '/receive-details',
                                 json=details)  # json=json.dumps(details).encode('utf-8'))
        self.check_status_code(response.status_code, 200)
        return response  # jsonify(response.json())

    def insert_into_network(self):
        id = self.get_id()

        details = {'id': id,
                   # 'wallet_public_key': self.wallet.get_public_key().decode('utf-8'),
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
        # response_dict = json.loads(response_json)
        # ama parw transaction_id kai telika den ginei validate to transaction prepei na meiwsw to transaction_id kata 1
        transaction_id = response_dict['transaction_id']

        # if self.wallet.balance() < amount:
        #     print("Node" + self.id + ": could not make transaction, not enough money!")
        # else:
        transaction_input, change = self.create_transaction_input(self.wallet.get_UTXOs(),
                                                                  self.wallet.get_public_key(), amount)

        if len(transaction_input) == 0:
            print("Not enough money for the transaction!")
            return False

        # print("Node with wallet public key:", receiver_address, "will receive ", amount, "NBC")
        # print("Node with wallet public key:", self.wallet.get_public_key(), "will have ", change,
        #       "NBC left in that transaction")

        response = requests.get(self.bootstrap_node_url + '/transaction-output-id')
        response_dict = response.json()
        # ama parw transaction_id kai telika den ginei validate to transaction prepei na meiwsw to transaction_id kata 1

        transaction_output_id1 = response_dict['transaction_output_id']
        if change != 0:
            response = requests.get(self.bootstrap_node_url + '/transaction-output-id')
            response_dict = response.json()
            # ama parw transaction_id kai telika den ginei validate to transaction prepei na meiwsw to transaction_id kata 1

            transaction_output_id2 = response_dict['transaction_output_id']
            transaction_output = [(transaction_output_id1, transaction_id, receiver_address, amount),
                                  (transaction_output_id2, transaction_id, self.wallet.get_public_key(), change)]
        else:
            transaction_output = [(transaction_output_id1, transaction_id, receiver_address, amount)]

        current_trans = Transaction(self.wallet.get_public_key(), transaction_id, transaction_input,
                                    transaction_output, self.wallet.get_private_key(), receiver_address, amount)


        # enhmerwtiko mhnyma !!!!!!!!!
        if self.broadcast_transaction(current_trans.to_dict()):
            self.wallet.update_utxo(current_trans.sender_address, current_trans.transaction_inputs,
                                    current_trans.transaction_output)

            self.blockchain.add_transaction(current_trans.to_dict()) #evala kai edw to_dict, den to eixame balei
            if len(self.blockchain.get_unmined_transactions()) >= self.blockchain.capacity and not self.is_mining:
                self.is_mining = True
                thread = threading.Thread(target=self.mine_block)
                thread.start()
                #thread.join()  #prosthesa auto gia sigouria
            return True

        else:
            response = requests.get(self.bootstrap_node_url + '/reduce-transaction-output-id')
            response_dict = response.json()
            if change != 0:
                response = requests.get(self.bootstrap_node_url + '/reduce-transaction-output-id')
                response_dict = response.json()

            print("Transaction is not valid!")
            return False

    # remember to broadcast it

    def send_transaction(self, node_url, trans_dict, responses):

        response = requests.post(node_url + '/receive-transaction', json=trans_dict)
        responses.append((response.json(), node_url))

    def broadcast_transaction(self, trans_dict):
        threads = []
        responses = []
        # network = main.app.config['nodes_details']
        for key, values in self.network.items():
            if str(key) != str(self.id):
                wallet_public_key, ip_address, port = values
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
                print("Invalid transaction! Node with public key" + trans_dict["sender_address"] + " has problem!" + node)
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
        validate_sign = self.verify_signature(trans["signature"], trans["sender_address"], trans["recipient_address"],
                                              trans["value"])

        if validate_sign:
            trans["transaction_inputs"] = [tuple(inner_list) for inner_list in trans["transaction_inputs"]]
            if set(trans["transaction_inputs"]).intersection(self.wallet.get_UTXOs()[trans["sender_address"]]) == set(
                    trans["transaction_inputs"]):
                self.wallet.update_utxo(trans["sender_address"], trans["transaction_inputs"],
                                        trans["transaction_outputs"])
                self.blockchain.add_transaction(trans)
                if len(self.blockchain.get_unmined_transactions()) >= self.blockchain.capacity and not self.is_mining:
                    self.is_mining = True
                    thread = threading.Thread(target=self.mine_block)
                    thread.start()
                    #thread.join()   #na to doume autoO!!O!O
                response = jsonify({"public_key": self.wallet.get_public_key(), "approve": True})
            else:
                print("Not enough amount for the transaction!")
                response = jsonify({"public_key": self.wallet.get_public_key(), "approve": False})
        else:
            print("Invalid sign on the transaction!")
            response = jsonify({"public_key": self.wallet.get_public_key(), "approve": False})
        return response

    #     def add_transaction_to_block():
    #
    #     # if enough transactions  mine
    #

    def execute_file_transactions(self, filepath):
        processed_transactions = 0
        counter=0
        print("Start of file transactions execution!")
        with open(filepath, 'r') as f:
            for line in f:
                processed_transactions+=1
                node_id, amount = line.split()
                node_id = node_id[2:]


                if node_id == self.id:
                    print("A node cannot send money to itself. Transaction aborted.")
                    continue

                amount = int(amount)  #KAI EDW NA DOUME MHPWS TO KANOUME FLOAT
                                      #PANTWS STA ARXEIA EXEI MONO INTS


                if amount <=0 :
                    print("Invalid amount. Amount must be a positive integer. Transaction aborted.")
                    continue

                # if amount > self.wallet.balance():  #aytos o elegxos ginetai kai metepeita sthn create_Transaction alla
                #                                     #mporei na mpei kai edw gia na mhn jalestei kan h create_transaction.
                #     print("Not enough money. Transaction aborted.")
                #     continue


                if int(node_id) < self.no_nodes: #na bgei auto!!!
                    while True:
                        response = requests.get(self.bootstrap_node_url + "/request_lock")
                        if response.status_code == 200:
                            if amount > self.wallet.balance():  # aytos o elegxos ginetai kai metepeita sthn create_Transaction alla
                                # mporei na mpei kai edw gia na mhn jalestei kan h create_transaction.
                                print("Not enough money. Transaction aborted.")
                                response = requests.get(self.bootstrap_node_url + "/release_lock")
                                if response.status_code == 400:
                                    print("Cannot release lock!") #isws to dw ayto
                                break
                            receiver_public_key = self.network[node_id][0]
                            self.create_transaction(receiver_public_key, amount)
                            counter+=1
                            response = requests.get(self.bootstrap_node_url + "/release_lock")
                            if response.status_code == 400:
                                print("Cannot release lock!")
                            break
                        else:
                            time.sleep(1)

        print("End of file transactions execution!")
        return processed_transactions

    def send_block(self, node_url, mined_block, responses):

        #print('NODE {} WILL SEND BLOCK TO NODE {}'.format(self.id,node_url))
        response = requests.post(node_url + '/receive-block', data=json.dumps(jsonpickle.encode(mined_block.to_dict())))
        #print("send block response: {} {}".format(response.status_code, response.json()))
        responses.append((response.json(), node_url))

    def broadcast_block(self, mined_block):
        threads = []
        responses = []
        # broadcast mined block to every node of the network
        for key, values in self.network.items():
            if str(key) != str(self.id):
                wallet_public_key, ip_address, port = values
                node_url = 'http://' + ip_address + ":" + port
                thread = threading.Thread(target=self.send_block, args=(node_url, mined_block, responses))
                threads.append(thread)
                thread.start()

    def mine_block(self):
        # check if unmined transactions have exceeded capacity
        if len(self.blockchain.get_unmined_transactions()) >= self.blockchain.capacity: #EDW AYTO ISWS NA BGEI EKTOS THS SYNARTHSHS,
                                                                                        #GIA NA MHN ANOIGOUME THREADS XWRIS LOGO
            current_chain_length = len(self.blockchain.chain)
            # calculate current chain length and pass it as arg to get_mined_block --> mine
            mined_block = self.blockchain.get_mined_block(chain_length=current_chain_length)
            # check if chain's last block remains the same - maybe block added by another node, additional check
            # and check if mined_block is not None - if None node did not complete mining and stopped
            # else node mined a block and broadcast it to the network
            if mined_block is not None and mined_block.previousHash == self.blockchain.get_last_block_hash():
                print("Nonce found.")
                self.blockchain.add_block(mined_block)
                self.broadcast_block(mined_block)

        self.is_mining = False
        if len(self.blockchain.get_unmined_transactions()) >= self.blockchain.capacity and not self.is_mining:
            self.is_mining = True
            t = threading.Thread(target=self.mine_block)
            t.start()
            #t.join()

    def validate_block(self, incoming_block):
        #print('----------------------------------------VALIDATE BLOCK----------------------------------------------')
        # return True
        # checks if hash is valid
        # case where transactions_to_mine have not been created yet
        # expected transactions = those that node would mine, and expects to be mined by others
        expected_transactions = self.blockchain.transactions_to_mine if len(
            self.blockchain.transactions_to_mine) > 0 else self.blockchain.transactions_unmined[
                                                           0:self.blockchain.capacity]
        # temp block contains:next index expected,expected transactions,expected previous hash,
        # incoming block's nonce, incoming block's timestamp
        temp_block = Block(len(self.blockchain.chain), expected_transactions, self.blockchain.get_last_block_hash(),
                           incoming_block.nonce, incoming_block.timestamp)
        # calculate expected hash
        expected_hash = temp_block.hash
        # recalculate incoming block's hash, in case its wrong
        temp_incoming_block = Block(incoming_block.index, incoming_block.listOfTransactions,
                                    incoming_block.previousHash,
                                    incoming_block.nonce, incoming_block.timestamp)
        # print("TRANSACGTIONS IN BLOCK:", incoming_block.listOfTransactions)
        # print("TRANSACGTIONS IN BLOCK:", temp_block.listOfTransactions)
        # print('HASHES EQUALITY {}'.format(temp_block.hash == incoming_block.hash))
        # print('BLOCKS PREV HASH IS EQUAL WITH INCOMING BLOCK PREV HASH {}'.format(temp_block.previousHash == incoming_block.previousHash))
        # print('BLOCKS NONCE IS EQUAL WITH INCOMING BLOCK NONCE {}'.format(temp_block.nonce == incoming_block.nonce))
        # print('BLOCKS TIMESTAMP IS EQUAL WITH INCOMING BLOCK TIMESTAMP {}'.format(temp_block.timestamp == incoming_block.timestamp))
        # print('BLOCKS HASH IS EQUAL WITH INCOMING BLOCK HASH {}'.format(temp_block.hash == incoming_block.hash))
        # # compare expected hash to incoming block's hash, if True block is valid
        # print('REHASH EQUALITY  {}'.format(temp_incoming_block.hash == incoming_block.hash))

        # print('DIFFICULTY ZEROS CHECK {}'.format(temp_incoming_block.hash[0:self.blockchain.difficulty] == ('0' * self.blockchain.difficulty)))
        # print('\n-----------------------------------TRANSACTIONS TO MINE -------------------------------------------------\n')
        # print('TRANSACTIONS TO MINE {}'.format(str(''.join(str(x) for x in temp_block.listOfTransactions)).encode('utf-8')))
        # print('\n-------------------------------------- -------------------------------------------------\n')
        # print('\n--------------------------------------INCOMING TRANSACTIONS MINED -------------------------------------------------\n')
        # print('TRANSACTIONS TO MINE {}'.format(str(''.join(str(x) for x in incoming_block.listOfTransactions)).encode('utf-8')))
        # print('\n----------------------------------------------------------------------------------------------------------\n')
        return temp_incoming_block.hash[0:self.blockchain.difficulty] == ('0' * self.blockchain.difficulty) and temp_incoming_block.hash == incoming_block.hash
        # return expected_hash == temp_incoming_block.hash and temp_incoming_block.hash[0:self.blockchain.difficulty] == (
        #             '0' * self.blockchain.difficulty)

    def get_chain(self, node_url, responses):
        response = requests.get(node_url + '/chain')
        responses.append(response)

    def resolve_conflict(self):
        #print('--------------RESOLVE CONFLICT-----------------------')
        #print(self.blockchain.chain)
        #exit()
        threads = []
        responses = []
        for key, values in self.network.items():
            if str(key) != str(self.id):
                wallet_public_key, ip_address, port = values
                node_url = 'http://' + ip_address + ":" + port
                thread = threading.Thread(target=self.get_chain, args=(node_url, responses))
                threads.append(thread)
                thread.start()
        # wait all threads to finish
        for t in threads:
            t.join()
        max_length = len(self.blockchain.chain)
        max_chain = self.blockchain.chain
        for response in responses:
            if response.status_code == 200:
                chain = jsonpickle.decode(response.json())
                length = len(chain)
                if max_length < length:
                    max_length = length
                    max_chain = chain
        self.blockchain.chain = max_chain

    # TODO: update balance?

    def validate_chain(self, bootstrap_chain):
        for b in bootstrap_chain[1:]:
            # calculate hash of every blo ck
            temp_block = Block(index=b.index, transactions=b.listOfTransactions, previousHash=b.previousHash,
                               timestamp=b.timestamp, nonce=b.nonce)
            # check if difficulty zeros and correct hashing
            if not (b.hash == temp_block.hash and temp_block.hash[0:self.blockchain.difficulty] == (
                    '0' * self.blockchain.difficulty)):
                return False
        return True

