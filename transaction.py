from collections import OrderedDict

import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import requests
from flask import Flask, jsonify, request, render_template


class Transaction:

    def __init__(self, sender_address, transaction_id,
                 transaction_inputs,  sender_private_key, recipient_address, value):
        # set
        # self.sender_address: #To public key του wallet από το οποίο προέρχονται τα χρήματα
        self.sender_address = sender_address
        # self.receiver_address: To public key του wallet στο οποίο θα καταλήξουν τα χρήματα
        self.receiver_address = recipient_address
        # self.amount: το ποσό που θα μεταφερθεί
        self.amount = value
        # self.transaction_id: το hash του transaction
        self.transaction_id = transaction_id
        # self.transaction_inputs: λίστα από Transaction Input
        self.transaction_inputs = transaction_inputs
        # self.transaction_outputs: λίστα από Transaction Output
        self.transaction_outputs = []
        # private_key
        self.sender_private_key = sender_private_key
        # signature
        self.signature = None

        self.transaction_outputs.append([self.transaction_id, self.receiver_address, self.amount])

    def to_dict(self):
        return OrderedDict({'transaction_id': self.transaction_id,
                            'sender_address': self.sender_address,
                            'recipient_address': self.receiver_address,
                            'transaction_inputs': self.transaction_inputs,
                            'transaction_outputs': self.transaction_outputs,
                            'value': self.amount,
                            'signature': self.signature})

    def sign_transaction(self):
        """
        Sign transaction with private key
        """
        transaction_data = str(self.sender_address) + str(self.receiver_address) + str(self.amount)
        transaction_hash = SHA256.new(transaction_data.encode())
        sign_key = RSA.importKey(binascii.unhexlify(self.sender_private_key))
        signer = PKCS1_v1_5.new(sign_key)
        signature = signer.sign(transaction_hash)
        self.signature = binascii.hexlify(signature).decode('ascii')
