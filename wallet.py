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
	def __init__(self, public_key, private_key, address, transactions):
		##set
		self.public_key = public_key
		self.private_key = private_key
		#self.transactions = transactions
		self.transactions = []  #[tuple1(-1 or 1, id, money), ...., ]
		self.address = address
		self.UTXOs = dict()

		#self.public_key
		#self.private_key
		#self_address
		#self.transactions

	def add_UTXO(self, wallet_public_key, transaction_id, NBC):
		if(wallet_public_key not in self.UTXOs):
			self.UTXOs[wallet_public_key] = [(transaction_id, NBC)]
		else:
			self.UTXOs[wallet_public_key] = self.UTXOs[wallet_public_key].append((transaction_id, NBC))


	def get_public_key(self):
		return self.public_key

	def get_private_key(self):
		return self.private_key

	def get_transactions(self):
		return self.transactions

	def get_address(self):
		return self.address
  
	def get_UTXOs(self):
		return self.UTXOs

	def balance(self):
		total_balance = 0
		for tr_id, nbc in self.UTXOs[self.public_key]:
			total_balance+=nbc
		return total_balance
