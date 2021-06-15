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
from crypto_dev_signer.eth.signer import ReferenceSigner as EIP155Signer
from crypto_dev_signer.keystore.dict import DictKeystore
from chainlib.chain import ChainSpec
from chainlib.eth.nonce import (
        RPCNonceOracle,
        OverrideNonceOracle,
        )
from chainlib.eth.gas import (
        RPCGasOracle,
        OverrideGasOracle,
        )
from chainlib.eth.connection import EthHTTPConnection
from chainlib.eth.tx import (
        receipt,
        TxFactory,
        )
from chainlib.eth.constant import ZERO_ADDRESS
from erc20_faucet.faucet import SingleShotFaucet 

# local imports
from erc20_faucet.faucet import SingleShotFaucet

logging.basicConfig(level=logging.WARNING)
logg = logging.getLogger()

script_dir = os.path.dirname(__file__)
data_dir = os.path.join(script_dir, '..', 'data')

default_eth_provider = os.environ.get('ETH_PROVIDER', 'http://localhost:8545')

argparser = argparse.ArgumentParser()
argparser.add_argument('-p', '--provider', dest='p', default=default_eth_provider, type=str, help='RPC provider url (http only)')
argparser.add_argument('-w', action='store_true', help='Wait for the last transaction to be confirmed')
argparser.add_argument('-ww', action='store_true', help='Wait for every transaction to be confirmed')
argparser.add_argument('-i', '--chain-spec', dest='i', type=str, default='evm:ethereum:1', help='Chain specification string')
argparser.add_argument('-y', '--key-file', dest='y', type=str, help='Ethereum keystore file to use for signing')
argparser.add_argument('-v', action='store_true', help='Be verbose')
argparser.add_argument('-vv', action='store_true', help='Be more verbose')
argparser.add_argument('--gas-price', type=int, dest='gas_price', help='Override gas price')
argparser.add_argument('-d', action='store_true', help='Dump RPC calls to terminal and do not send')
argparser.add_argument('--nonce', type=int, help='Override transaction nonce')
argparser.add_argument('--overrider-address', type=str, dest='overrider_address', help='Overrider address')
argparser.add_argument('--env-prefix', default=os.environ.get('CONFINI_ENV_PREFIX'), dest='env_prefix', type=str, help='environment prefix for variables to overwrite configuration')
argparser.add_argument('--account-index-address', type=str, dest='account_index_address', help='Account index contract address')
argparser.add_argument('token_address', type=str, help='Mintable token address')
args = argparser.parse_args()

if args.vv:
    logg.setLevel(logging.DEBUG)
elif args.v:
    logg.setLevel(logging.INFO)

block_last = args.w
block_all = args.ww

passphrase_env = 'ETH_PASSPHRASE'
if args.env_prefix != None:
    passphrase_env = args.env_prefix + '_' + passphrase_env
passphrase = os.environ.get(passphrase_env)
if passphrase == None:
    logg.warning('no passphrase given')
    passphrase=''

signer_address = None
keystore = DictKeystore()
if args.y != None:
    logg.debug('loading keystore file {}'.format(args.y))
    signer_address = keystore.import_keystore_file(args.y, password=passphrase)
    logg.debug('now have key for signer address {}'.format(signer_address))
signer = EIP155Signer(keystore)

chain_spec = ChainSpec.from_chain_str(args.i)

rpc = EthHTTPConnection(args.p)
nonce_oracle = None
if args.nonce != None:
    nonce_oracle = OverrideNonceOracle(signer_address, args.nonce)
else:
    nonce_oracle = RPCNonceOracle(signer_address, rpc)

gas_oracle = None
if args.gas_price !=None:
    gas_oracle = OverrideGasOracle(price=args.gas_price, conn=rpc, code_callback=SingleShotFaucet.gas)
else:
    gas_oracle = RPCGasOracle(rpc, code_callback=SingleShotFaucet.gas)

dummy = args.d

token_address = args.token_address
overrider_address = signer_address
if args.overrider_address != None:
    overrider_address = args.overrider_address
account_index_address = args.account_index_address
if account_index_address == None:
    account_index_address = ZERO_ADDRESS


def main():
    c = SingleShotFaucet(chain_spec, signer=signer, nonce_oracle=nonce_oracle, gas_oracle=gas_oracle)
    (tx_hash_hex, o) = c.store_constructor(signer_address)
    if dummy:
        print(tx_hash_hex)
        print(o)
    else:
        rpc.do(o)
        r = rpc.wait(tx_hash_hex)
        if r['status'] == 0:
            sys.stderr.write('EVM revert while deploying contract. Wish I had more to tell you')
            sys.exit(1)
        # TODO: pass through translator for keys (evm tester uses underscore instead of camelcase)
        store_address = r['contractAddress']
        logg.info('deployed faucet store on {}'.format(store_address))

        c = SingleShotFaucet(chain_spec, signer=signer, gas_oracle=gas_oracle, nonce_oracle=nonce_oracle)
        (tx_hash_hex, o) = c.constructor(signer_address, token_address, store_address, account_index_address, [overrider_address])
        rpc.do(o)
        r = rpc.wait(tx_hash_hex)
        if r['status'] == 0:
            sys.stderr.write('EVM revert while deploying contract. Wish I had more to tell you')
            sys.exit(1)
        # TODO: pass through translator for keys (evm tester uses underscore instead of camelcase)
        address = r['contractAddress']

        if block_last:
            rpc.wait(tx_hash_hex)

        print(address)


if __name__ == '__main__':
    main()
