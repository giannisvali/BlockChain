# import blockchain
import datetime
import time
import hashlib


class Block:
    def __init__(self, index, transactions, previousHash='', nonce=0,
                 timestamp=datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), hash=None):
        self.index = index
        self.previousHash = previousHash
        self.timestamp = timestamp
        self.listOfTransactions = transactions
        self.nonce = nonce
        self.hash = self.my_hash() if hash is None else hash

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

    def mine(self, difficulty, chain_length, chain):
        difficulty_zeros = '0' * difficulty
        print('initial chain length {}'.format(chain_length))
        print('initial chain {}'.format(chain))
        print('mining started')
        while self.hash[0:difficulty] != difficulty_zeros:
            self.nonce += 1
            self.hash = self.my_hash()
            if chain_length < len(chain):
                print('Mining stopped')
                return

        print('mining successful : finished with hash {} and nonce {}'.format(self.hash, self.nonce))

    def to_dict(self):
        return {
            'index': self.index,
            'previous_hash': self.previousHash,
            'timestamp': self.timestamp,
            'transactions': self.listOfTransactions,
            'nonce': self.nonce,
            'hash': self.hash
        }

    def __str__(self):
        return ("Index: {}\nPreviousHash: {}\nTimestamp: {}\nHash: {}\nNonce: {}\nTransactions: {}".format(
                    self.index,
                    self.previousHash,
                    self.timestamp,
                    self.hash,
                    self.nonce,
                    "\n".join(str(x) for x in self.listOfTransactions)))

# if __name__ == '__main__':
#     block = Block(1,[1,2,3],'23hgf5')
#     block.mine(2)
