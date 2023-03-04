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
		self.transactions = transactions
		#self.public_key
		#self.private_key
		#self_address
		#self.transactions

	def get_public_key(self):
		return self.public_key

	def get_private_key(self):
		return self.private_key

	def get_transactions(self):
		return self.transactions


	def balance():

