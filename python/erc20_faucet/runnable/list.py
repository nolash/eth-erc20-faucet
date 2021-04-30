"""Query faucet store

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
from crypto_dev_signer.eth.helper import EthTxExecutor
from chainlib.chain import ChainSpec
from chainlib.eth.nonce import RPCNonceOracle
from chainlib.eth.gas import RPCGasOracle
from chainlib.eth.connection import EthHTTPConnection
from chainlib.eth.tx import receipt
from chainlib.eth.constant import ZERO_CONTENT
from chainlib.error import JSONRPCException

# local imports
from erc20_faucet import Faucet

logging.basicConfig(level=logging.WARNING)
logg = logging.getLogger()

script_dir = os.path.dirname(__file__)
data_dir = os.path.join(script_dir, '..', 'data')

default_format = 'terminal'

argparser = argparse.ArgumentParser()
argparser.add_argument('-p', '--provider', dest='p', default='http://localhost:8545', type=str, help='RPC provider url (http only)')
argparser.add_argument('-i', '--chain-spec', dest='i', type=str, default='evm:ethereum:1', help='Chain specification string')
argparser.add_argument('-a', '--contract-address', dest='a', required=True, type=str, help='Faucet store contract address')
argparser.add_argument('-f', '--format', dest='f', type=str, default=default_format, help='Output format [human, brief]')
argparser.add_argument('-v', action='store_true', help='Be verbose')
argparser.add_argument('-vv', action='store_true', help='Be more verbose')
argparser.add_argument('--env-prefix', default=os.environ.get('CONFINI_ENV_PREFIX'), dest='env_prefix', type=str, help='environment prefix for variables to overwrite configuration')
argparser.add_argument('address', type=str, help='Address to check faucet usage for')
args = argparser.parse_args()

if args.vv:
    logg.setLevel(logging.DEBUG)
elif args.v:
    logg.setLevel(logging.INFO)

chain_spec = ChainSpec.from_chain_str(args.i)

rpc = EthHTTPConnection(args.p)
faucet_store_address = args.a
address = args.address
fmt = args.f


def out_element(e, fmt=default_format, w=sys.stdout):
    logg.debug('format {}'.format(fmt))
    if fmt == 'brief':
        w.write(str(e[1]) + '\n')
    else:
        w.write('{} {}\n'.format(e[0], e[1]))


def element(ifc, address, fmt=default_format, w=sys.stdout):
    o = ifc.usable_for(faucet_store_address, address)
    r =  rpc.do(o)
    have = ifc.parse_usable_for(r)
    out_element((address, have), fmt, w)


def main():
    c = Faucet(chain_spec)
    element(c, address, fmt=fmt, w=sys.stdout)


if __name__ == '__main__':
    main()
