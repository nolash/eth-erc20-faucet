"""Deploys sarafu faucet contract

.. moduleauthor:: Louis Holbrook <dev@holbrook.no>
.. pgp:: 0826EDA1702D1E87C6E2875121D2E7BB88C2A746 

"""

# standard imports
import sys
import os
import json
import argparse
import logging

# external imports
import chainlib.eth.cli
from chainlib.chain import ChainSpec
from chainlib.eth.connection import EthHTTPConnection
from chainlib.eth.tx import (
        receipt,
        TxFactory,
        )
from chainlib.eth.constant import ZERO_ADDRESS
from chainlib.eth.address import to_checksum_address
from hexathon import (
        add_0x,
        strip_0x,
        )

# local imports
from erc20_faucet.faucet import SingleShotFaucet

logging.basicConfig(level=logging.WARNING)
logg = logging.getLogger()

arg_flags = chainlib.eth.cli.argflag_std_write
argparser = chainlib.eth.cli.ArgumentParser(arg_flags)
argparser.add_argument('--overrider-address', type=str, dest='overrider_address', default=ZERO_ADDRESS, help='Overrider address')
argparser.add_argument('--account-index-address', type=str, dest='account_index_address', default=ZERO_ADDRESS, help='Account index contract address')
argparser.add_argument('--store-address', type=str, dest='store_address', help='Faucet store address')
argparser.add_argument('token_address', type=str, help='Mintable token address')
args = argparser.parse_args()

extra_args = {
    'overrider_address': None,
    'account_index_address': None,
    'store_address': None,
    'token_address': None,
    }
config = chainlib.eth.cli.Config.from_args(args, arg_flags, extra_args=extra_args, default_fee_limit=SingleShotFaucet.gas())

wallet = chainlib.eth.cli.Wallet()
wallet.from_config(config)

rpc = chainlib.eth.cli.Rpc(wallet=wallet)
conn = rpc.connect_by_config(config)

chain_spec = ChainSpec.from_chain_str(config.get('CHAIN_SPEC'))
args = argparser.parse_args()


def main():
    signer = rpc.get_signer()
    signer_address = rpc.get_sender_address()

    gas_oracle = rpc.get_gas_oracle()
    nonce_oracle = rpc.get_nonce_oracle()

    c = SingleShotFaucet(chain_spec, signer=signer, nonce_oracle=nonce_oracle, gas_oracle=gas_oracle)

    store_address = None
    try:
        store_address = to_checksum_address(config.get('_STORE_ADDRESS'))
        if not config.true('_UNSAFE') and store_address != add_0x(config.get('_STORE_ADDRESS')):
            raise ValueError('invalid checksum address for store')
        logg.debug('using store address {}'.format(store_address))
    except TypeError:
        pass

    account_index_address = to_checksum_address(config.get('_ACCOUNT_INDEX_ADDRESS'))
    if not config.true('_UNSAFE') and account_index_address != add_0x(config.get('_ACCOUNT_INDEX_ADDRESS')):
        raise ValueError('invalid checksum address for account index address')

    token_address = None
    try:
        token_address = to_checksum_address(config.get('_TOKEN_ADDRESS'))
        if not config.true('_UNSAFE') and token_address != add_0x(config.get('_TOKEN_ADDRESS')):
            raise ValueError('invalid checksum address for token address')
    except TypeError:
        pass

    overrider_address = to_checksum_address(config.get('_OVERRIDER_ADDRESS'))
    if not config.true('_UNSAFE') and overrider_address != add_0x(config.get('_OVERRIDER_ADDRESS')):
        raise ValueError('invalid checksum address for overrider address')


    if store_address == None:
        (tx_hash_hex, o) = c.store_constructor(signer_address)
        if not config.get('_WAIT'):
            print(o)
        else:
            conn.do(o)
            r = conn.wait(tx_hash_hex)
            if r['status'] == 0:
                sys.stderr.write('EVM revert while deploying contract. Wish I had more to tell you')
                sys.exit(1)
            # TODO: pass through translator for keys (evm tester uses underscore instead of camelcase)
            store_address = r['contractAddress']
            logg.info('deployed faucet store on {}'.format(store_address))
            print(store_address)

    if store_address != None:
        c = SingleShotFaucet(chain_spec, signer=signer, gas_oracle=gas_oracle, nonce_oracle=nonce_oracle)
        (tx_hash_hex, o) = c.constructor(signer_address, token_address, store_address, account_index_address, [overrider_address])
        conn.do(o)
        if config.get('_WAIT'):
            r = conn.wait(tx_hash_hex)
            if r['status'] == 0:
                sys.stderr.write('EVM revert while deploying contract. Wish I had more to tell you')
                sys.exit(1)
            # TODO: pass through translator for keys (evm tester uses underscore instead of camelcase)
            address = r['contractAddress']

            print(address)
        else:
            print(tx_hash_hex)


if __name__ == '__main__':
    main()
