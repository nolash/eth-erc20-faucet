# standard imports
import logging

# external imports
from chainlib.eth.tx import TxFactory
from chainlib.eth.constant import ZERO_ADDRESS
from chainlib.eth.contract import (
        abi_decode_single,
        ABIContractEncoder,
        ABIContractType,
        )
from chainlib.eth.tx import (
        TxFormat,
        )
from chainlib.jsonrpc import jsonrpc_template
from hexathon import add_0x

logg = logging.getLogger().getChild(__name__)


class Faucet(TxFactory):

    def give_to(self, contract_address, sender_address, beneficiary_address, tx_format=TxFormat.JSONRPC):
        enc = ABIContractEncoder()
        enc.method('giveTo')
        enc.typ(ABIContractType.ADDRESS)
        enc.address(beneficiary_address)
        data = enc.get()
        tx = self.template(sender_address, contract_address, use_nonce=True)
        tx = self.set_code(tx, data)
        tx = self.finalize(tx, tx_format)
        return tx


    def set_amount(self, contract_address, sender_address, amount, tx_format=TxFormat.JSONRPC):
        enc = ABIContractEncoder()
        enc.method('setAmount')
        enc.typ(ABIContractType.UINT256)
        enc.uint256(amount)
        data = enc.get()
        tx = self.template(sender_address, contract_address, use_nonce=True)
        tx = self.set_code(tx, data)
        tx = self.finalize(tx, tx_format)
        return tx


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


    def token_amount(self, contract_address, block_height=None, sender_address=ZERO_ADDRESS):
        o = jsonrpc_template()
        o['method'] = 'eth_call'
        enc = ABIContractEncoder()
        enc.method('tokenAmount')
        data = add_0x(enc.get())
        tx = self.template(sender_address, contract_address)
        tx = self.set_code(tx, data)
        o['params'].append(self.normalize(tx))

        if block_height != None:
            o['params'].append(block_height)

        return o


    @classmethod
    def parse_token_amount(self, v):
        return abi_decode_single(ABIContractType.UINT256, v)
