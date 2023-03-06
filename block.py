
# import blockchain
import datetime
import time
from Crypto.Hash import SHA256



class Block:
	def __init__(self, index, Transactions, previousHash = ''):
		self.index=index
		self.previousHash = previousHash
		self.timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
		self.hash = self.myHash()
		self.nonce = 0
		self.listOfTransactions = Transactions
	
	def myHash(self):
		#calculate self.hash
		hash = SHA256.new()
		trans = "||".join(map(str, self.listOfTransactions))
		block_string = str.encode(str(self.timestamp) + trans + str(self.previousHash) + str(self.nonce))
		hash.update(block_string)
		return hash.hexdigest()


	#def add_transaction(transaction transaction, blockchain blockchain):
		#add a transaction to the block

	# def to_dict(self):
	# 	return OrderedDict({'Index': self.index,
	# 						'Timestamp': self.timestamp,
	# 						'Transactions': self.listOfTransactions,
	# 						'Nonce': self.nonce,
	# 						'PreviousHash': self.previousHash,
	# 						'CurrentHash': self.currentHash})

	# def mine(self, difficulty):
	# 	self.currentHash = self.calculate_hash()
	# 	check = "".join(["0" for i in range(difficulty)])
	# 	print("Mining....")
	# 	while (self.currentHash[:difficulty] != check):
	# 		self.nonce += 1
	# 		self.currentHash = self.calculate_hash()
	# 	print("Mining Completed !!!")
	#
	# def isValid(self, difficulty):
	# 	check = "".join(["0" for i in range(difficulty)])
	# 	return ((self.currentHash[:difficulty] == check) and (self.currentHash == self.calculate_hash()))
	#
	# def __str__(self):
	# 	return ("Index: {}\nTimestamp: {}\nTransactions: \n{}\nPreviousHash: {}\nNonce: {}\nHash: {}".format(self.index,
	# 																										 self.timestamp,
	# 																										 "\n".join(
	# 																											 map(str,
	# 																												 self.listOfTransactions)),
	# 																										 self.previousHash,
	# 																										 self.nonce,
	# 																										 self.currentHash))

