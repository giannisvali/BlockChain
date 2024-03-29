import json

from block import Block
import datetime


class Blockchain:

    def __init__(self, capacity=5, difficulty=3):
        self.chain = []  # keep list of blocks
        self.difficulty = difficulty
        self.capacity = capacity
        self.transactions_unmined = []  # keep list of transactions not mined yet
        self.transactions_to_mine = []
        self.block_timestamps = []


    def set_chain(self, chain):
        self.chain = chain

    def set_unmined_transactions(self, unmined_transactions):
        self.transactions_unmined = unmined_transactions
    def chain_to_dict(self):
        chain = []
        for block in self.chain:
            chain.append(block.to_dict())
        return chain
    # insert block to chain
    def add_block(self, block, timestamp = True):
        # self.Hash_set.add(block.currentHash)
        self.chain.append(block)
        if timestamp:
            self.block_timestamps.append(datetime.datetime.now())

    #  add transaction to the list of unmined tranasactions
    def add_transaction(self, transaction):
        # json dumps here avoid differences in hashes (parenthesis-bracket)
        self.transactions_unmined.append(json.dumps(transaction))
        # self.pendingTransactions.append(transaction)

    def get_last_block_hash(self):
        return self.chain[-1].hash

    def get_last_block(self):
        return self.chain[-1]

    # kathe fora pou simplironontai capacity transactions
    # creates new block, updates list of transactions not mined and starts mining
    # returns the mined block
    def get_mined_block(self, chain_length):
        # index of the new block ( end of chain)
        block_to_mine_index = len(self.chain)
        # from transactions not mined yet keep first "capacity" of them
        self.transactions_to_mine = self.transactions_unmined[0:self.capacity]
        # create block with transactions_to_mine
        block_to_mine = Block(index=block_to_mine_index, transactions=self.transactions_to_mine, previousHash=self.get_last_block_hash())
        # update transactions not yet mined
        self.transactions_unmined = self.transactions_unmined[self.capacity:]
        # start block mining, pass as arg chain length calculated and chain of node
        mining_completed = block_to_mine.mine(self.difficulty, chain_length, self.chain)
        # reset transactions_to_mine
        self.transactions_to_mine = []
        if mining_completed:
            return block_to_mine
        else:
            return None

    def get_unmined_transactions(self):
        return self.transactions_unmined

    def hash_exists_in_chain(self, hash):
        for block in self.chain:
            if block.hash == hash:
                return True
        return False


    def __str__(self):
        return (''.join(str(b) for b in self.chain))

