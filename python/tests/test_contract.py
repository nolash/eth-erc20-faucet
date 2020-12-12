import os
import unittest
import json
import logging

import web3
import eth_tester
import eth_abi

logging.basicConfig(level=logging.DEBUG)
logg = logging.getLogger()

logging.getLogger('web3').setLevel(logging.WARNING)
logging.getLogger('eth.vm').setLevel(logging.WARNING)

testdir = os.path.dirname(__file__)


class Test(unittest.TestCase):

    contract = None

    def setUp(self):
        eth_params = eth_tester.backends.pyevm.main.get_default_genesis_params({
            'gas_limit': 9000000,
            })

        # create store of used accounts
        f = open(os.path.join(testdir, '../erc20_single_shot_faucet/data/ERC20SingleShotFaucetStorage.bin'), 'r')
        bytecode = f.read()
        f.close()

        f = open(os.path.join(testdir, '../erc20_single_shot_faucet/data/ERC20SingleShotFaucetStorage.abi.json'), 'r')
        self.abi_storage = json.load(f)
        f.close()


        backend = eth_tester.PyEVMBackend(eth_params)
        self.eth_tester =  eth_tester.EthereumTester(backend)
        provider = web3.Web3.EthereumTesterProvider(self.eth_tester)
        self.w3 = web3.Web3(provider)
        c = self.w3.eth.contract(abi=self.abi_storage, bytecode=bytecode)
        tx_hash = c.constructor().transact({'from': self.w3.eth.accounts[0]})

        r = self.w3.eth.getTransactionReceipt(tx_hash)

        self.address_storage = r.contractAddress


        # create token
        f = open(os.path.join(testdir, '../erc20_single_shot_faucet/data/GiftableToken.bin'), 'r')
        bytecode = f.read()
        f.close()

        f = open(os.path.join(testdir, '../erc20_single_shot_faucet/data/GiftableToken.abi.json'), 'r')
        self.abi_token = json.load(f)
        f.close()

        t = self.w3.eth.contract(abi=self.abi_token, bytecode=bytecode)
        tx_hash = t.constructor('Foo Token', 'FOO', 18).transact({'from': self.w3.eth.accounts[0]})

        r = self.w3.eth.getTransactionReceipt(tx_hash)

        self.address_token = r.contractAddress
        t = self.w3.eth.contract(abi=self.abi_token, address=self.address_token)

        tx_hash = t.functions.mint(1000).transact({'from': self.w3.eth.accounts[0]})


        # create faucet
        f = open(os.path.join(testdir, '../erc20_single_shot_faucet/data/ERC20SingleShotFaucet.bin'), 'r')
        bytecode = f.read()
        f.close()

        f = open(os.path.join(testdir, '../erc20_single_shot_faucet/data/ERC20SingleShotFaucet.abi.json'), 'r')
        self.abi_faucet = json.load(f)
        f.close()

#        f = open(os.path.join(testdir, '../erc20_single_shot_faucet/data/ERC20SingleShotFaucet.abi.json'), 'r')
#        abi_storage_interface = json.load(f)
#        f.close()

        c = self.w3.eth.contract(abi=self.abi_faucet, bytecode=bytecode)
        tx_hash = c.constructor([
                self.w3.eth.accounts[1],
                self.w3.eth.accounts[2],
            ],
            self.address_token,
            self.address_storage,
            ).transact({'from': self.w3.eth.accounts[0]})

        r = self.w3.eth.getTransactionReceipt(tx_hash)

        self.address_faucet = r.contractAddress
        c = self.w3.eth.contract(abi=self.abi_faucet, address=self.address_faucet)

        tx_hash = t.functions.transfer(self.address_faucet, 100).transact({'from': self.w3.eth.accounts[0]})


    def tearDown(self):
        pass


    def test_basic(self):
        c = self.w3.eth.contract(abi=self.abi_faucet, address=self.address_faucet)
        self.assertTrue(c.functions.setAmount(10).transact({'from': self.w3.eth.accounts[0]}))
        self.assertTrue(c.functions.setAmount(20).transact({'from': self.w3.eth.accounts[1]}))
        with self.assertRaises(Exception):
            c.functions.setAmount(30).transact({'from': self.w3.eth.accounts[3]})


    def test_giveto(self):
        c = self.w3.eth.contract(abi=self.abi_faucet, address=self.address_faucet)
        c.functions.setAmount(10).transact({'from': self.w3.eth.accounts[2]})
        c.functions.giveTo(self.w3.eth.accounts[3]).transact({'from': self.w3.eth.accounts[1]})

        t = self.w3.eth.contract(abi=self.abi_token, address=self.address_token)
        self.assertEqual(t.functions.balanceOf(self.w3.eth.accounts[3]).call(), 10);
        self.assertEqual(t.functions.balanceOf(self.address_faucet).call(), 90);

        with self.assertRaises(Exception):
            c.functions.giveTo(self.w3.eth.accounts[3]).transact({'from': self.w3.eth.accounts[1]})

        c.functions.setAmount(50).transact({'from': self.w3.eth.accounts[1]})
        c.functions.giveTo(self.w3.eth.accounts[4]).transact({'from': self.w3.eth.accounts[1]})
        self.assertEqual(t.functions.balanceOf(self.w3.eth.accounts[4]).call(), 50);
        self.assertEqual(t.functions.balanceOf(self.address_faucet).call(), 40);

        with self.assertRaises(Exception):
            c.functions.giveTo(self.w3.eth.accounts[5]).transact({'from': self.w3.eth.accounts[1]})
        self.assertEqual(t.functions.balanceOf(self.w3.eth.accounts[5]).call(), 0);
        self.assertEqual(t.functions.balanceOf(self.address_faucet).call(), 40);



