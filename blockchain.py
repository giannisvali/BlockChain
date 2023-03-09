from block import Block


class Blockchain:

    def __init__(self, capacity=5):
        self.chain = []  # keep list of blocks
        self.difficulty = 4
        self.capacity = capacity
        self.transactions_unmined = []  # keep list of transactions not mined yet
        # self.Hash_set = set()

    # insert block to chain
    def add_block(self, block):
        # self.Hash_set.add(block.currentHash)
        self.chain.append(block)

    #  add transaction to the list of unmined tranasactions
    def add_transaction(self, transaction):
        self.transactions_unmined.append(transaction)
        # self.pendingTransactions.append(transaction)

    def get_last_block_hash(self):
        return self.chain[-1].hash

    def get_last_block(self):
        return self.chain[-1]

    # kathe fora pou simplironontai capacity transactions
    # creates new block, updates list of transactions not mined and starts mining
    # returns the mined block
    def get_mined_block(self):
        block_to_mine_index = len(self.chain)
        block_to_mine_transactions = self.transactions_unmined[0:self.capacity]
        block_to_mine = Block(block_to_mine_index, block_to_mine_transactions, self.get_last_block_hash())
        self.transactions_unmined = self.transactions_unmined[self.capacity:]  # update transactions not yet mined
        block_to_mine.mine(self.difficulty)
        return block_to_mine

    def __str__(self):
        return (''.join(str(b) for b in self.chain))


# if __name__ == '__main__':
#     blockchain = Blockchain()
#     # genesis block
#     blockchain.add_block(Block(1,[00,80,99,99,11],'23hgf5'))
#     for i in range(8):
#         blockchain.add_transaction(i)
#     block1 = blockchain.get_mined_block()
#     blockchain.add_block(block1)
#     print(blockchain)
#     print(blockchain.transactions_unmined)