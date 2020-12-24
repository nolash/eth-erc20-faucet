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


logging.basicConfig(level=logging.WARNING)
logg = logging.getLogger()

logging.getLogger('web3').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

script_dir = os.path.dirname(__file__)
data_dir = os.path.join(script_dir, '..', 'data')

argparser = argparse.ArgumentParser()
argparser.add_argument('-p', '--provider', dest='p', default='http://localhost:8545', type=str, help='Web3 provider url (http only)')
argparser.add_argument('-a', '--approvers', dest='a', action='append', type=str, help='Approver account to add')
argparser.add_argument('-o', '--owner', dest='o', type=str, help='Owner account (provider must have private key)')
argparser.add_argument('-t', '--token-address', dest='t', required=True, type=str, help='Token to add faucet for')
argparser.add_argument('--set-amount', dest='amount', default=0, type=int, help='Initial amount to set. Will be 0 if not set!')
argparser.add_argument('-i', '--account-index-address', dest='i', required=False, type=str, help='Accounts index to verify requesting address against (if not specified, any address may use the faucet')
argparser.add_argument('--abi-dir', dest='abi_dir', type=str, default=data_dir, help='Directory containing bytecode and abi (default: {})'.format(data_dir))
argparser.add_argument('-v', action='store_true', help='Be verbose')
args = argparser.parse_args()

if args.v:
    logg.setLevel(logging.DEBUG)

def main():
    w3 = web3.Web3(web3.Web3.HTTPProvider(args.p))
    w3.eth.defaultAccount = w3.eth.accounts[0]
    if args.o != None:
        w3.eth.defaultAccount = web3.Web3.toChecksumAddress(args.o)

    token_address = args.t

    f = open(os.path.join(args.abi_dir, 'ERC20SingleShotFaucetStorage.json'), 'r')
    abi = json.load(f)
    f.close()

    f = open(os.path.join(args.abi_dir, 'ERC20SingleShotFaucetStorage.bin'), 'r')
    bytecode = f.read()
    f.close()

    c = w3.eth.contract(abi=abi, bytecode=bytecode)
    tx_hash = c.constructor().transact()
    r = w3.eth.getTransactionReceipt(tx_hash)
    store_address = r.contractAddress

    f = open(os.path.join(args.abi_dir, 'ERC20SingleShotFaucet.json'), 'r')
    abi = json.load(f)
    f.close()

    f = open(os.path.join(args.abi_dir, 'ERC20SingleShotFaucet.bin'), 'r')
    bytecode = f.read()
    f.close()

    c = w3.eth.contract(abi=abi, bytecode=bytecode)

    approvers = [w3.eth.accounts[0]]
    if args.a != None:
        for a in args.a:
            approvers.append(a)
            logg.info('add approver {}'.format(a))

    accounts_index_address = '0x0000000000000000000000000000000000000000'
    if args.i != None:
        accounts_index_address = args.i

    tx_hash = c.constructor(approvers, token_address, store_address, accounts_index_address).transact()
    rcpt = w3.eth.getTransactionReceipt(tx_hash)
    address = rcpt.contractAddress

    if args.amount > 0:
        c = w3.eth.contract(abi=abi, address=address)
        tx_hash = c.functions.setAmount(args.amount).transact()
        logg.debug('setting initial ammount to {} tx_hash {}'.format(args.amount, tx_hash))
        r = w3.eth.getTransactionReceipt(tx_hash)
        amount = c.functions.amount().call()
        logg.info('set initial ammount tx_hash {}'.format(amount))

    print(address)


if __name__ == '__main__':
    main()
