# import blockchain
import datetime
import time
import hashlib
from collections import OrderedDict


class Block:
    def __init__(self, index, transactions, previousHash=''):
        self.index = index
        self.previousHash = previousHash
        self.timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        self.listOfTransactions = transactions
        self.nonce = 0
        self.hash = self.my_hash()



    def get_previousHash(self):
        return self.previousHash

    # calculates hash of the block using nonce, its transactions, prev hash and timestamp
    def my_hash(self):
        hash = hashlib.sha256()
        # TODO: consider addition of __str__ in transaction class
        data = ''.join(str(x) for x in self.listOfTransactions)
        hash.update(
            str(self.nonce).encode('utf-8') +
            str(data).encode('utf-8') +
            str(self.previousHash).encode('utf-8') +
            str(self.timestamp).encode('utf-8')
        )
        return hash.hexdigest()

    def mine(self, difficulty):
        difficulty_zeros = '0' * difficulty
        print('mining started')
        while self.hash[0:difficulty] != difficulty_zeros:
            self.nonce += 1
            self.hash = self.my_hash()
        print('mining finished with hash {} and nonce {}'.format(self.hash, self.nonce))

    def __str__(self):
        return ("\n---------------BLOCK-----------------------\n"
                + "Index: {}\nPreviousHash: {}\nTimestamp: {}\nHash: {}\nNonce: {}\nTransactions: {}".format(
                    self.index,
                    self.previousHash,
                    self.timestamp,
                    self.hash,
                    self.nonce,
                    "\n".join(str(x) for x in self.listOfTransactions)))


    def to_dict(self):
        return OrderedDict({'index': self.index,
                            'previousHash': self.previousHash,
                            'timestamp': self.timestamp,
                            'listOfTransactions': self.listOfTransactions,
                            'nonce': self.nonce,
                            'hash': self.hash})
