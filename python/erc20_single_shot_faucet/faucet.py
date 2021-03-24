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
