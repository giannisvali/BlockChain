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
                 transaction_input, transaction_output, sender_private_key, recipient_address, value):

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
        self.transaction_inputs = transaction_input  # transaction_inputs
        # self.transaction_outputs: λίστα από Transaction Output
        self.transaction_output = []
        self.transaction_output = transaction_output
        # private_key
        self.sender_private_key = sender_private_key
        # signature
        self.signature = None

        # amount_left = self.amount
        # change = 0
        # UTXO =
        # for tr_id, public_key, NBC in transaction_inputs:
        #     if public_key == self.sender_address:
        #         amount_left -= NBC
        #         if amount_left - NBC <= 0:
        #             change = NBC - amount_left
        #             break
        #
        # if amount_left > 0:
        #     print("Not enough money for the transaction!")
        # else:
        #     print("Node with wallet public key:", self.receiver_address, "will receive ", self.amount, "NBC")
        #     print("Node with wallet public key:", self.sender_address, "will have ", change,
        #           "NBC left in that transaction")
        #     if change != 0:
        #         self.transaction_outputs = [(self.transaction_id, self.receiver_address, self.amount),
        #                                     (self.transaction_id, self.sender_address, change)]
        #     else:
        #         self.transaction_outputs = [(self.transaction_id, self.receiver_address, self.amount)]

        self.signature = self.sign_transaction()

    def to_dict(self):
        return OrderedDict({'transaction_id': self.transaction_id,
                            'sender_address': self.sender_address,
                            'recipient_address': self.receiver_address,
                            'transaction_inputs': self.transaction_inputs,
                            'transaction_outputs': self.transaction_output,
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
        return binascii.hexlify(signature).decode('ascii')
