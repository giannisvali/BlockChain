import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4


class Wallet:
	def __init__(self, public_key, private_key, address, boodstrap_public):
		##set
		self.public_key = public_key
		self.private_key = private_key
		self.address = address
		self.UTXOs = dict()

		# self.public_key
		# self.private_key
		# self_address
		# self.transactions

	def update_utxo(self, sender, transaction_input, transaction_output):
		for item in transaction_input:
			if item in self.UTXOs[sender]:
				self.UTXOs[sender].remove(item)
		for transaction_id, address, amount in transaction_output:
			if address not in self.UTXOs:
				self.UTXOs[address] = [(transaction_id, amount)]
			else:
				self.UTXOs[address] = self.UTXOs[address].append((transaction_id, amount))

	def get_public_key(self):
		return self.public_key

	def get_private_key(self):
		return self.private_key

	def get_address(self):
		return self.address

	def get_UTXOs(self):
		return self.UTXOs

	def balance(self):
		total_balance = 0
		for tr_id, nbc in self.UTXOs[self.public_key]:
			total_balance += nbc
		return total_balance
