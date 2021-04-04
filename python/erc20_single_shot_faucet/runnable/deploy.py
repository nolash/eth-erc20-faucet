"""Deploys erc20 single shot faucet

.. moduleauthor:: Louis Holbrook <dev@holbrook.no>
.. pgp:: 0826EDA1702D1E87C6E2875121D2E7BB88C2A746 

"""

# standard imports
import os
import json
import argparse
import logging

# third-party imports
import web3
from crypto_dev_signer.eth.signer import ReferenceSigner as EIP155Signer
from crypto_dev_signer.keystore import DictKeystore
from crypto_dev_signer.eth.helper import EthTxExecutor

logging.basicConfig(level=logging.WARNING)
logg = logging.getLogger()

logging.getLogger('web3').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

script_dir = os.path.dirname(__file__)
data_dir = os.path.join(script_dir, '..', 'data')

argparser = argparse.ArgumentParser()
argparser.add_argument('-p', '--provider', dest='p', default='http://localhost:8545', type=str, help='Web3 provider url (http only)')
argparser.add_argument('-w', action='store_true', help='Wait for the last transaction to be confirmed')
argparser.add_argument('-ww', action='store_true', help='Wait for every transaction to be confirmed')
argparser.add_argument('-i', '--chain-spec', dest='i', type=str, default='Ethereum:1', help='Chain specification string')
argparser.add_argument('--editor', action='append', type=str, help='Amount editor account to add')
argparser.add_argument('-a', '--signer-address', dest='a', type=str, help='Owner account (provider must have private key)')
argparser.add_argument('-y', '--key-file', dest='y', type=str, help='Ethereum keystore file to use for signing')
argparser.add_argument('--token-address', dest='token_address', required=True, type=str, help='Token to add faucet for')
argparser.add_argument('--set-amount', dest='set_amount', default=0, type=int, help='Initial amount to set. Will be 0 if not set!')
argparser.add_argument('--accounts-index-address', dest='accounts_index_address', required=False, type=str, help='Accounts index to verify requesting address against (if not specified, any address may use the faucet')
argparser.add_argument('--abi-dir', dest='abi_dir', type=str, default=data_dir, help='Directory containing bytecode and abi (default: {})'.format(data_dir))
argparser.add_argument('-v', action='store_true', help='Be verbose')
argparser.add_argument('-vv', action='store_true', help='Be more verbose')
args = argparser.parse_args()

if args.vv:
    logg.setLevel(logging.DEBUG)
elif args.v:
    logg.setLevel(logging.INFO)

block_last = args.w
block_all = args.ww

w3 = web3.Web3(web3.Web3.HTTPProvider(args.p))

signer_address = None
keystore = DictKeystore()
if args.y != None:
    logg.debug('loading keystore file {}'.format(args.y))
    signer_address = keystore.import_keystore_file(args.y)
    logg.debug('now have key for signer address {}'.format(signer_address))
signer = EIP155Signer(keystore)


chain_pair = args.i.split(':')
chain_id = int(chain_pair[1])

helper = EthTxExecutor(
        w3,
        signer_address,
        signer,
        chain_id,
        block=args.ww,
    )


def main():
    token_address = args.token_address

    f = open(os.path.join(args.abi_dir, 'ERC20SingleShotFaucetStorage.json'), 'r')
    abi = json.load(f)
    f.close()

    f = open(os.path.join(args.abi_dir, 'ERC20SingleShotFaucetStorage.bin'), 'r')
    bytecode = f.read()
    f.close()

    c = w3.eth.contract(abi=abi, bytecode=bytecode)
    (tx_hash, rcpt) = helper.sign_and_send(
            [
                c.constructor().buildTransaction
                ],
            force_wait=True,
            )
    store_address = rcpt.contractAddress

    f = open(os.path.join(args.abi_dir, 'ERC20SingleShotFaucet.json'), 'r')
    abi = json.load(f)
    f.close()

    f = open(os.path.join(args.abi_dir, 'ERC20SingleShotFaucet.bin'), 'r')
    bytecode = f.read()
    f.close()

    c = w3.eth.contract(abi=abi, bytecode=bytecode)

    editors = [signer_address]
    if args.editor != None:
        for a in args.editor:
            editors.append(a)
            logg.info('add approver {}'.format(a))

    accounts_index_address = '0x0000000000000000000000000000000000000000'
    if args.accounts_index_address != None:
        accounts_index_address = args.accounts_index_address

    (tx_hash, rcpt) = helper.sign_and_send(
            [
                c.constructor(editors, token_address, store_address, accounts_index_address).buildTransaction,
                ],
                force_wait=True,
            )
    address = rcpt.contractAddress

    if args.set_amount > 0:
        c = w3.eth.contract(abi=abi, address=address)
        (tx_hash, rcpt) = helper.sign_and_send(
            [
                c.functions.setAmount(args.set_amount).buildTransaction,
                ],
            force_wait=True,
            )
        
        logg.debug('setting initial ammount to {} tx_hash {}'.format(args.set_amount, tx_hash))
        amount = c.functions.amount().call()
        logg.info('set initial ammount tx_hash {}'.format(amount))

    print(address)


if __name__ == '__main__':
    main()
