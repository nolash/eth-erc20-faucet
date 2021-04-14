# Author:	Louis Holbrook <dev@holbrook.no> 0826EDA1702D1E87C6E2875121D2E7BB88C2A746
# SPDX-License-Identifier:	GPL-3.0-or-later
# File-version: 1
# Description: Python interface to abi and bin files for faucet contracts

# standard imports
import logging
import json
import os

# external imports
from chainlib.eth.tx import TxFactory
from chainlib.eth.constant import ZERO_ADDRESS
from chainlib.eth.contract import (
        abi_decode_single,
        ABIContractEncoder,
        ABIContractType,
        )
from chainlib.jsonrpc import jsonrpc_template
from hexathon import add_0x

logg = logging.getLogger()

moddir = os.path.dirname(__file__)
datadir = os.path.join(moddir, 'data')


class SingleShotFaucet(TxFactory):

    __abi = None
    __bytecode = None
    __address = None

    @staticmethod
    def abi(part=None):
        if SingleShotFaucet.__abi == None:
            f = open(os.path.join(datadir, 'ERC20SingleShotFaucet.json'), 'r')
            SingleShotFaucet.__abi = json.load(f)
            f.close()
        if part == 'storage':
            f = open(os.path.join(datadir, 'ERC20SingleShotFaucetStorage.json'))
            abi = f.read()
            f.close()
            return abi
        elif part != None:
            raise ValueError('unknown abi identifier "{}"'.format(part))
        return SingleShotFaucet.__abi


    @staticmethod
    def bytecode(part=None):
        if SingleShotFaucet.__bytecode == None:
            f = open(os.path.join(datadir, 'ERC20SingleShotFaucet.bin'))
            SingleShotFaucet.__bytecode = f.read()
            f.close()
        if part == 'storage':
            f = open(os.path.join(datadir, 'ERC20SingleShotFaucetStorage.bin'))
            bytecode = f.read()
            f.close()
            return bytecode
        elif part != None:
            raise ValueError('unknown bytecode identifier "{}"'.format(part))

        return SingleShotFaucet.__bytecode


    def store_constructor(self, sender_address):
        code = SingleShotFaucet.bytecode(part='storage')
        tx = self.template(sender_address, None, use_nonce=True)
        tx = self.set_code(tx, code)
        return self.build(tx)


    def usable_for(self, contract_address, address, sender_address=ZERO_ADDRESS):
        o = jsonrpc_template()
        o['method'] = 'eth_call'
        enc = ABIContractEncoder()
        enc.method('cooldown')
        enc.typ(ABIContractType.ADDRESS)
        enc.address(address)
        data = add_0x(enc.get())
        tx = self.template(sender_address, contract_address)
        tx = self.set_code(tx, data)
        o['params'].append(self.normalize(tx))
        return o


    @classmethod
    def parse_usable_for(self, v):
        r = abi_decode_single(ABIContractType.UINT256, v)
        return r == 0

 
    def token(self, contract_address, sender_address=ZERO_ADDRESS):
        o = jsonrpc_template()
        o['method'] = 'eth_call'
        enc = ABIContractEncoder()
        enc.method('token')
        data = add_0x(enc.get())
        tx = self.template(sender_address, contract_address)
        tx = self.set_code(tx, data)
        o['params'].append(self.normalize(tx))
        return o

   
    @classmethod
    def parse_token(self, v):
        return abi_decode_single(ABIContractType.ADDRESS, v)


    def amount(self, contract_address, block_height=None, sender_address=ZERO_ADDRESS):
        o = jsonrpc_template()
        o['method'] = 'eth_call'
        enc = ABIContractEncoder()
        enc.method('amount')
        data = add_0x(enc.get())
        tx = self.template(sender_address, contract_address)
        tx = self.set_code(tx, data)
        o['params'].append(self.normalize(tx))

        if block_height != None:
            o['params'].append(block_height)

        return o


    @classmethod
    def parse_amount(self, v):
        return abi_decode_single(ABIContractType.UINT256, v)
