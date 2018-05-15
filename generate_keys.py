#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Crypto import Random
from Crypto.PublicKey import RSA


modulus_length = 1024*4

privatekey = RSA.generate(modulus_length, Random.new().read)
publickey = privatekey.publickey()

print("private key:")
print(privatekey.exportKey())
print("-------------------------")
print("public key:")
print(publickey.exportKey())

fp = open("private_key.pk", "wb")
fp.write(privatekey.exportKey())
fp.close()

fp = open("public_key.pub", "wb")
fp.write(publickey.exportKey())
fp.close()


