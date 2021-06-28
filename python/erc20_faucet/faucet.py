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
from hexathon import add_0x

# local imports
from .interface import Faucet

logg = logging.getLogger().getChild(__name__)

moddir = os.path.dirname(__file__)
datadir = os.path.join(moddir, 'data')


class SingleShotFaucet(Faucet):

    __abi = None
    __bytecode = None
    __address = None

    @staticmethod
    def abi(part=None):
        if SingleShotFaucet.__abi == None:
            f = open(os.path.join(datadir, 'ERC20Faucet.json'), 'r')
            SingleShotFaucet.__abi = json.load(f)
            f.close()
        if part == 'storage':
            f = open(os.path.join(datadir, 'ERC20FaucetStorage.json'))
            abi = f.read()
            f.close()
            return abi
        elif part != None:
            raise ValueError('unknown abi identifier "{}"'.format(part))
        return SingleShotFaucet.__abi


    @staticmethod
    def bytecode(part=None):
        if SingleShotFaucet.__bytecode == None:
            f = open(os.path.join(datadir, 'ERC20Faucet.bin'))
            SingleShotFaucet.__bytecode = f.read()
            f.close()
        if part == 'storage':
            f = open(os.path.join(datadir, 'ERC20FaucetStorage.bin'))
            bytecode = f.read()
            f.close()
            return bytecode
        elif part != None:
            raise ValueError('unknown bytecode identifier "{}"'.format(part))

        return SingleShotFaucet.__bytecode


    @staticmethod
    def gas(code=None):
        return 2000000


    def store_constructor(self, sender_address):
        code = SingleShotFaucet.bytecode(part='storage')
        tx = self.template(sender_address, None, use_nonce=True)
        tx = self.set_code(tx, code)
        return self.build(tx)


    # TODO: allow multiple overriders
    def constructor(self, sender_address, token, store, accounts_index, overrider):
        if accounts_index == None:
            accounts_index = ZERO_ADDRESS
        code = SingleShotFaucet.bytecode()
        enc = ABIContractEncoder()
        enc.uint256(0x80)
        enc.address(token)
        enc.address(store)
        enc.address(accounts_index)
        enc.uint256(len(overrider))
        for r in overrider:
            enc.address(r)
        code += enc.get()
        tx = self.template(sender_address, None, use_nonce=True)
        tx = self.set_code(tx, code)
        return self.build(tx)
