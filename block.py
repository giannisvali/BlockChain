# import blockchain
import datetime
import time
import hashlib
from collections import OrderedDict


class Block:
    def __init__(self, index, transactions, previousHash='', nonce=0,
                 timestamp=datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), hash=None):
        self.index = index
        self.previousHash = previousHash
        self.timestamp = timestamp
        self.listOfTransactions = transactions
        self.nonce = nonce
        self.hash = self.my_hash() if hash is None else hash



    def get_previousHash(self):
        return self.previousHash

    # calculates hash of the block using nonce, its transactions, prev hash and timestamp
    def my_hash(self):
        hash = hashlib.sha256()
        # TODO: consider possible changes depending on type of transaction (Transaction vs dictionary)
        data = ''.join(str(x) for x in self.listOfTransactions)
        hash.update(
            str(self.nonce).encode('utf-8') +
            str(data).encode('utf-8') +
            str(self.previousHash).encode('utf-8') +
            str(self.timestamp).encode('utf-8')
        )
        return hash.hexdigest()

    def mine(self, difficulty, chain_length, chain):
        difficulty_zeros = '0' * difficulty
        print('initial chain length {}'.format(chain_length))
        print('initial chain {}'.format(chain))
        print('mining started')
        # check if first difficulty characters of hash are zeros
        while self.hash[0:difficulty] != difficulty_zeros:
            self.nonce += 1
            self.hash = self.my_hash()
            # compare initial chain length with current chain length
            # if chain length greater another node mined the block --> stop mining
            if chain_length < len(chain):
                print('Mining stopped, another node mined the block')
                return False #stopped

        print('mining successful : finished with hash {} and nonce {}'.format(self.hash, self.nonce))
        return True #completed

    def to_dict(self):
        return OrderedDict({
            'index': self.index,
            'previous_hash': self.previousHash,
            'timestamp': self.timestamp,
            'transactions': self.listOfTransactions,
            'nonce': self.nonce,
            'hash': self.hash
        })

    def __str__(self):
        return ("Index: {}\nPreviousHash: {}\nTimestamp: {}\nHash: {}\nNonce: {}\nTransactions: {}".format(
                    self.index,
                    self.previousHash,
                    self.timestamp,
                    self.hash,
                    self.nonce,
                    "\n".join(str(x) for x in self.listOfTransactions)))


    # def to_dict(self):
    #     return OrderedDict({'index': self.index,
    #                         'previousHash': self.previousHash,
    #                         'timestamp': self.timestamp,
    #                         'listOfTransactions': self.listOfTransactions,
    #                         'nonce': self.nonce,
    #                         'hash': self.hash})
