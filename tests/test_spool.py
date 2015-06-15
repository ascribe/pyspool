import unittest
import os
import random
import requests

from string import ascii_letters
from spool import Wallet
from spool import File
from spool import Spool
from transactions import Transactions
from spool import BlockchainSpider

requests.packages.urllib3.disable_warnings()

"""
History:

1. Refill Federation wallet with necessary fuel and tokens
2. user1 registers master edition
3. user1 registers number of editions
4. user1 registers edition number 1
5. user1 transferes edition number 1 to user2
6. user2 consigns edition number 1 to user 3
7. user3 unconsigns edition number 1 to user2
8. user2 loans edition number 1 to user 3
"""


class TestSpool(unittest.TestCase):

    def setUp(self):
        try:
            # flag to run the tests
            test = os.environ['TEST_SPOOL']
            if test == '2':
                username = os.environ['TESTNET_USERNAME']
                password = os.environ['TESTNET_PASSWORD']
                host = os.environ['TESTNET_HOST']
                port = os.environ['TESTNET_PORT']
            self.refill_pass = os.environ['TEST_REFILL_PASS']
            self.federation_pass = os.environ['TEST_FEDERATION_PASS']
            self.refill_root = Wallet(self.refill_pass, testnet=True).root_address
            self.federation_root = Wallet(self.federation_pass, testnet=True).root_address
        except KeyError:
            raise unittest.SkipTest('TEST_REFILL_PASS and/or TEST_FEDERATION_PASS environment variables are not set.')

        # set TEST_SPOOL=2 to test with bitcoind
        if test == '2':
            print 'using bitcoind'
            self.t = Transactions(testnet=True, service='daemon', username=username, password=password, host=host, port=port)
            self.spool = Spool(testnet=True, service='daemon', username=username, password=password, host=host, port=port)
        else:
            print 'using blockr'
            self.t = Transactions(testnet=True)
            self.spool = Spool(testnet=True)

        self.user1_pass = self._get_pass()
        self.user2_pass = self._get_pass()
        self.user3_pass = self._get_pass()
        self.user1_root = Wallet(self.user1_pass, testnet=True).root_address
        self.user1_leaf = Wallet(self.user1_pass, testnet=True).address_from_path()
        self.user2_leaf = Wallet(self.user2_pass, testnet=True).address_from_path()
        self.user3_leaf = Wallet(self.user3_pass, testnet=True).address_from_path()
        self.file_hash = self._get_file_hash()

        print 'user1_pass: ', self.user1_pass
        print 'user2_pass: ', self.user2_pass
        print 'user3_pass: ', self.user3_pass
        print 'user1_root: ', self.user1_root
        print 'user1_leaf: ', self.user1_leaf
        print 'user2_leaf: ', self.user2_leaf
        print 'user3_leaf: ', self.user3_leaf
        print 'file_hash :', self.file_hash

        self.spool._t.import_address(self.user1_root[1], "test",)
        self.spool._t.import_address(self.user1_leaf[1], "test",)
        self.spool._t.import_address(self.user2_leaf[1], "test",)
        self.spool._t.import_address(self.user3_leaf[1], "test",)
        self.spool._t.import_address(self.file_hash[0], "test",)
        self.spool._t.import_address(self.file_hash[1], "test",)


    def test_spool(self):
        # 1. Refill Federation wallet with necessary fuel and tokens
        print
        print 'Refilling Federation wallet with necessary fuel and tokens'
        txid = self.spool.refill_main_wallet(self.refill_root, self.federation_root[1], 7, 11, self.refill_pass,
                                             min_confirmations=1, sync=True)
        print txid

        # 2. user1 registers master edition
        print
        print 'user1 registers master edition'
        txid = self.spool.register(self.federation_root, self.user1_root[1], self.file_hash,
                                   self.federation_pass, 0, min_confirmations=1, sync=True)
        print txid

        tx = self.t.get(txid)
        verb = BlockchainSpider.check_script(tx['vouts'])
        self.assertEqual(verb, 'ASCRIBESPOOL01REGISTER0')

        # 3. user1 registers number of editions
        print
        print 'user1 registers number of editions'
        txid = self.spool.editions(self.federation_root, self.user1_root[1], self.file_hash,
                                   self.federation_pass, 10, min_confirmations=1, sync=True)
        print txid

        tx = self.t.get(txid)
        verb = BlockchainSpider.check_script(tx['vouts'])
        self.assertEqual(verb, 'ASCRIBESPOOL01EDITIONS10')

        # 4. user1 registers edition number 1
        print
        print 'user1 registers edition number 1'
        txid = self.spool.register(self.federation_root, self.user1_leaf[1], self.file_hash,
                                   self.federation_pass, 1, min_confirmations=1, sync=True)
        print txid

        tx = self.t.get(txid)
        verb = BlockchainSpider.check_script(tx['vouts'])
        self.assertEqual(verb, 'ASCRIBESPOOL01REGISTER1')

        # 5. Refill user1 wallet before transfer
        print
        print 'Refill user1 wallet before transfer'
        txid = self.spool.refill(self.federation_root, self.user1_leaf[1], 1, 1,
                                 self.federation_pass, min_confirmations=1, sync=True)
        print txid

        # 5. User1 transfers edition number 1 to user2
        print
        print 'User1 transfers edition number 1 to user 2'
        txid = self.spool.transfer(self.user1_leaf, self.user2_leaf[1], self.file_hash,
                                   self.user1_pass, 1, min_confirmations=1, sync=True)
        print txid

        tx = self.t.get(txid)
        verb = BlockchainSpider.check_script(tx['vouts'])
        self.assertEqual(verb, 'ASCRIBESPOOL01TRANSFER1')

        # 6. Refill user2 wallet before consign
        print
        print 'Refill user2 wallet before consign'
        txid = self.spool.refill(self.federation_root, self.user2_leaf[1], 1, 1,
                                 self.federation_pass, min_confirmations=1, sync=True)
        print txid

        # 6. user2 consigns edition number 1 to user3
        print
        print 'user2 consigns edition number 1 to user3'
        txid = self.spool.consign(self.user2_leaf, self.user3_leaf[1], self.file_hash,
                                  self.user2_pass, 1, min_confirmations=1, sync=True)
        print txid

        tx = self.t.get(txid)
        verb = BlockchainSpider.check_script(tx['vouts'])
        self.assertEqual(verb, 'ASCRIBESPOOL01CONSIGN1')

        # 7. Refill user3 wallet before unconsign
        print
        print 'Refill user3 wallet before unconsign'
        txid = self.spool.refill(self.federation_root, self.user3_leaf[1], 1, 1,
                                 self.federation_pass, min_confirmations=1, sync=True)
        print txid

        # 7. user3 unconsigns edition number 1 to user2
        print
        print 'user3 unconsigns edition number 1 back to user2'
        txid = self.spool.unconsign(self.user3_leaf, self.user2_leaf[1], self.file_hash,
                                    self.user3_pass, 1, min_confirmations=1, sync=True)
        print txid

        tx = self.t.get(txid)
        verb = BlockchainSpider.check_script(tx['vouts'])
        self.assertEqual(verb, 'ASCRIBESPOOL01UNCONSIGN1')

        # 8. Refill user2 wallet before loan
        print
        print 'Refill user2 wallet before loan'
        txid = self.spool.refill(self.federation_root, self.user2_leaf[1], 1, 1,
                                 self.federation_pass, min_confirmations=1, sync=True)
        print txid

        # 8. user2 loans edition number 1 to user3
        print
        print 'user2 loans edition number 1 to user3'
        txid = self.spool.loan(self.user2_leaf, self.user3_leaf[1], self.file_hash,
                               self.user2_pass, 1, '150522', '150523', min_confirmations=1, sync=True)
        print txid

        tx = self.t.get(txid)
        verb = BlockchainSpider.check_script(tx['vouts'])
        self.assertEqual(verb, 'ASCRIBESPOOL01LOAN1/150522150523')

    def _get_pass(self):
        return ''.join([random.choice(ascii_letters) for i in xrange(10)])

    def _get_file_hash(self):
        title = ''.join([random.choice(ascii_letters) for i in xrange(10)])
        with open('/tmp/test', 'w') as f:
            f.write(random._urandom(100))

        f = File('/tmp/test', testnet=True, title=title)
        return f.file_hash, f.file_hash_metadata