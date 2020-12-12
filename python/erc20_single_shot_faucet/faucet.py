# Author:	Louis Holbrook <dev@holbrook.no> 0826EDA1702D1E87C6E2875121D2E7BB88C2A746
# SPDX-License-Identifier:	GPL-3.0-or-later
# File-version: 1
# Description: Python interface to abi and bin files for faucet contracts

# standard imports
import logging
import json
import os

logging.basicConfig(level=logging.DEBUG)
logg = logging.getLogger()

moddir = os.path.dirname(__file__)
datadir = os.path.join(moddir, 'data')


class Faucet:

    __abi = None
    __bytecode = None

    def __init__(self, w3, address, signer_address=None):
        abi = Faucet.abi()
        Faucet.bytecode()
        self.address =address
        self.contract = w3.eth.contract(abi=abi, address=self.address)
        self.w3 = w3
        if signer_address != None:
            self.signer_address = signer_address
        else:
            if type(self.w3.eth.defaultAccount).__name__ == 'Empty':
                self.w3.eth.defaultAccount = self.w3.eth.accounts[0]
            self.signer_address = self.w3.eth.defaultAccount


    @staticmethod
    def abi(part=None):
        if Faucet.__abi == None:
            f = open(os.path.join(datadir, 'ERC20SingleShotFaucet.json'), 'r')
            Faucet.__abi = json.load(f)
            f.close()
        if part == 'storage':
            f = open(os.path.join(datadir, 'ERC20SingleShotFaucetStorage.json'))
            abi = f.read()
            f.close()
            return abi
        elif part != None:
            raise ValueError('unknown abi identifier "{}"'.format(part))
        return Faucet.__abi


    @staticmethod
    def bytecode(part=None):
        if Faucet.__bytecode == None:
            f = open(os.path.join(datadir, 'ERC20SingleShotFaucet.bin'))
            Faucet.__bytecode = f.read()
            f.close()
        if part == 'storage':
            f = open(os.path.join(datadir, 'ERC20SingleShotFaucetStorage.bin'))
            bytecode = f.read()
            f.close()
            return bytecode
        elif part != None:
            raise ValueError('unknown bytecode identifier "{}"'.format(part))

        return Faucet.__bytecode

    
    def give_to(self, address):
        tx_hash = self.contract.functions.giveTo(address).transact({
            'from': self.signer_address,
        })
        return tx_hash


    def address():
        return self.address
