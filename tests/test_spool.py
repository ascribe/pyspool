from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from future import standard_library
standard_library.install_aliases()
from builtins import range

import codecs
import os
import random
import requests
import unittest
from queue import Queue
from string import ascii_letters
from uuid import uuid1

import pytest
from pycoin.key.BIP32Node import BIP32Node
from transactions import Transactions

from spool import BlockchainSpider, File, Spool, Wallet

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
            print('using bitcoind')
            self.t = Transactions(testnet=True, service='daemon', username=username, password=password, host=host, port=port)
            self.spool = Spool(testnet=True, service='daemon', username=username, password=password, host=host, port=port)
        else:
            print('using blockr')
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

        print('user1_pass: ', self.user1_pass)
        print('user2_pass: ', self.user2_pass)
        print('user3_pass: ', self.user3_pass)
        print('user1_root: ', self.user1_root)
        print('user1_leaf: ', self.user1_leaf)
        print('user2_leaf: ', self.user2_leaf)
        print('user3_leaf: ', self.user3_leaf)
        print('file_hash :', self.file_hash)

        self.spool._t.import_address(self.user1_root[1], "test",)
        self.spool._t.import_address(self.user1_leaf[1], "test",)
        self.spool._t.import_address(self.user2_leaf[1], "test",)
        self.spool._t.import_address(self.user3_leaf[1], "test",)
        self.spool._t.import_address(self.file_hash[0], "test",)
        self.spool._t.import_address(self.file_hash[1], "test",)


    def test_spool(self):
        # 1. Refill Federation wallet with necessary fuel and tokens
        print()
        print('Refilling Federation wallet with necessary fuel and tokens')
        txid = self.spool.refill_main_wallet(self.refill_root, self.federation_root[1], 7, 11, self.refill_pass,
                                             min_confirmations=1, sync=True)
        print(txid)

        # 2. user1 registers master edition
        print()
        print('user1 registers master edition')
        txid = self.spool.register(self.federation_root, self.user1_root[1], self.file_hash,
                                   self.federation_pass, 0, min_confirmations=1, sync=True)
        print(txid)

        tx = self.t.get(txid)
        verb = BlockchainSpider.check_script(tx['vouts'])
        self.assertEqual(verb, 'ASCRIBESPOOL01REGISTER0')

        # 3. user1 registers number of editions
        print()
        print('user1 registers number of editions')
        txid = self.spool.editions(self.federation_root, self.user1_root[1], self.file_hash,
                                   self.federation_pass, 10, min_confirmations=1, sync=True)
        print(txid)

        tx = self.t.get(txid)
        verb = BlockchainSpider.check_script(tx['vouts'])
        self.assertEqual(verb, 'ASCRIBESPOOL01EDITIONS10')

        # 4. user1 registers edition number 1
        print()
        print('user1 registers edition number 1')
        txid = self.spool.register(self.federation_root, self.user1_leaf[1], self.file_hash,
                                   self.federation_pass, 1, min_confirmations=1, sync=True)
        print(txid)

        tx = self.t.get(txid)
        verb = BlockchainSpider.check_script(tx['vouts'])
        self.assertEqual(verb, 'ASCRIBESPOOL01REGISTER1')

        # 5. Refill user1 wallet before transfer
        print()
        print('Refill user1 wallet before transfer')
        txid = self.spool.refill(self.federation_root, self.user1_leaf[1], 1, 1,
                                 self.federation_pass, min_confirmations=1, sync=True)
        print(txid)

        # 5. User1 transfers edition number 1 to user2
        print()
        print('User1 transfers edition number 1 to user 2')
        txid = self.spool.transfer(self.user1_leaf, self.user2_leaf[1], self.file_hash,
                                   self.user1_pass, 1, min_confirmations=1, sync=True)
        print(txid)

        tx = self.t.get(txid)
        verb = BlockchainSpider.check_script(tx['vouts'])
        self.assertEqual(verb, 'ASCRIBESPOOL01TRANSFER1')

        # 6. Refill user2 wallet before consign
        print()
        print('Refill user2 wallet before consign')
        txid = self.spool.refill(self.federation_root, self.user2_leaf[1], 1, 1,
                                 self.federation_pass, min_confirmations=1, sync=True)
        print(txid)

        # 6. user2 consigns edition number 1 to user3
        print()
        print('user2 consigns edition number 1 to user3')
        txid = self.spool.consign(self.user2_leaf, self.user3_leaf[1], self.file_hash,
                                  self.user2_pass, 1, min_confirmations=1, sync=True)
        print(txid)

        tx = self.t.get(txid)
        verb = BlockchainSpider.check_script(tx['vouts'])
        self.assertEqual(verb, 'ASCRIBESPOOL01CONSIGN1')

        # 7. Refill user3 wallet before unconsign
        print()
        print('Refill user3 wallet before unconsign')
        txid = self.spool.refill(self.federation_root, self.user3_leaf[1], 1, 1,
                                 self.federation_pass, min_confirmations=1, sync=True)
        print(txid)

        # 7. user3 unconsigns edition number 1 to user2
        print()
        print('user3 unconsigns edition number 1 back to user2')
        txid = self.spool.unconsign(self.user3_leaf, self.user2_leaf[1], self.file_hash,
                                    self.user3_pass, 1, min_confirmations=1, sync=True)
        print(txid)

        tx = self.t.get(txid)
        verb = BlockchainSpider.check_script(tx['vouts'])
        self.assertEqual(verb, 'ASCRIBESPOOL01UNCONSIGN1')

        # 8. Refill user2 wallet before loan
        print()
        print('Refill user2 wallet before loan')
        txid = self.spool.refill(self.federation_root, self.user2_leaf[1], 1, 1,
                                 self.federation_pass, min_confirmations=1, sync=True)
        print(txid)

        # 8. user2 loans edition number 1 to user3
        print()
        print('user2 loans edition number 1 to user3')
        txid = self.spool.loan(self.user2_leaf, self.user3_leaf[1], self.file_hash,
                               self.user2_pass, 1, '150522', '150523', min_confirmations=1, sync=True)
        print(txid)

        tx = self.t.get(txid)
        verb = BlockchainSpider.check_script(tx['vouts'])
        self.assertEqual(verb, 'ASCRIBESPOOL01LOAN1/150522150523')

    def _get_pass(self):
        return ''.join([random.choice(ascii_letters) for i in range(10)])

    def _get_file_hash(self):
        title = ''.join([random.choice(ascii_letters) for i in range(10)])
        with open('/tmp/test', 'w') as f:
            f.write(random._urandom(100))

        f = File('/tmp/test', testnet=True, title=title)
        return f.file_hash, f.file_hash_metadata


def test_spool_class_init_default():
    from spool import Spool
    spool = Spool()
    assert spool.testnet is False
    assert spool._netcode == 'BTC'
    assert isinstance(spool._t, Transactions)
    assert spool._t._service.name == 'BitcoinBlockrService'
    assert spool._t.testnet is False
    assert isinstance(spool._spents, Queue)
    assert spool._spents.maxsize == 50


@pytest.mark.usefixtures('init_blockchain')
def test_simple_spool_transaction(spool_regtest, rpconn):
    alice, bob = rpconn.getnewaddress(), rpconn.getnewaddress()
    rpconn.sendtoaddress(alice, spool_regtest.FEE/100000000)
    rpconn.sendtoaddress(alice, spool_regtest.TOKEN/100000000)
    rpconn.generate(1)
    tx = spool_regtest.simple_spool_transaction(
        alice, (bob,), 'ascribespool123verb', min_confirmations=1)
    assert tx


def test_no_funds_select_inputs(spool_regtest, rpconn):
    addr = rpconn.getnewaddress()
    with pytest.raises(Exception) as exc:
        spool_regtest.select_inputs(addr, 1, 1)
    assert exc.value.args[0] == 'No spendable outputs found'


@pytest.mark.usefixtures('init_blockchain')
def test_insufficient_funds_select_inputs(spool_regtest, rpconn):
    from spool.spool import SpoolFundsError
    addr = rpconn.getnewaddress()
    rpconn.sendtoaddress(addr, 1)
    rpconn.generate(1)
    with pytest.raises(SpoolFundsError) as exc:
        spool_regtest.select_inputs(addr, 1, 1, min_confirmations=1)
    assert isinstance(exc.value, SpoolFundsError)
    assert (exc.value.message ==
            'Not enough outputs to spend. Refill your wallet')


@pytest.mark.usefixtures('init_blockchain')
def test_select_inputs(spool_regtest, rpconn):
    from spool import Spool
    addr = rpconn.getnewaddress()
    txid_fee = rpconn.sendtoaddress(addr, Spool.FEE/100000000)
    txid_token = rpconn.sendtoaddress(addr, Spool.TOKEN/100000000)
    rpconn.generate(1)
    inputs = spool_regtest.select_inputs(addr, 1, 1, min_confirmations=1)
    assert len(inputs) == 2
    fee_input = inputs[0]       # NOTE: assumes fees are first
    token_input = inputs[1]     # NOTE: assumes tokens are last
    assert fee_input['txid'] == txid_fee
    assert fee_input['amount'] == Spool.FEE
    assert fee_input['confirmations'] == 1
    assert token_input['txid'] == txid_token
    assert token_input['amount'] == Spool.TOKEN
    assert token_input['confirmations'] == 1
    assert spool_regtest._spents.qsize() == 2
    assert spool_regtest._spents.get() == fee_input
    assert spool_regtest._spents.get() == token_input


@pytest.mark.usefixtures('init_blockchain')
def test_clear_spents_queue_select_inputs(spool_regtest, rpconn):
    from spool import Spool
    addr = rpconn.getnewaddress()
    txid_fee = rpconn.sendtoaddress(addr, Spool.FEE/100000000)
    txid_token = rpconn.sendtoaddress(addr, Spool.TOKEN/100000000)
    rpconn.generate(1)
    spool_regtest.SPENTS_QUEUE_MAXSIZE = 2
    spool_regtest._spents.put('dummy')
    inputs = spool_regtest.select_inputs(addr, 1, 1, min_confirmations=1)
    assert len(inputs) == 2
    fee_input = inputs[0]       # NOTE: assumes fees are first
    token_input = inputs[1]     # NOTE: assumes tokens are last
    assert fee_input['txid'] == txid_fee
    assert fee_input['amount'] == Spool.FEE
    assert fee_input['confirmations'] == 1
    assert token_input['txid'] == txid_token
    assert token_input['amount'] == Spool.TOKEN
    assert token_input['confirmations'] == 1
    assert spool_regtest._spents.qsize() == 2
    assert spool_regtest._spents.get() == fee_input
    assert spool_regtest._spents.get() == token_input


@pytest.mark.usefixtures('init_blockchain')
def test_refill_main_wallet(spool_regtest, rpconn):
    src_wallet_passowrd = uuid1().hex.encode('utf-8')
    src_wallet = BIP32Node.from_master_secret(src_wallet_passowrd,
                                              netcode='XTN')
    dest_wallet_passowrd = uuid1().hex.encode('utf-8')
    dest_wallet = BIP32Node.from_master_secret(dest_wallet_passowrd,
                                               netcode='XTN')
    src_address = src_wallet.bitcoin_address()
    dest_address = dest_wallet.bitcoin_address()
    rpconn.importaddress(src_address)
    rpconn.importaddress(dest_address)
    rpconn.sendtoaddress(src_address, 1)
    rpconn.generate(1)
    txid = spool_regtest.refill_main_wallet(
        ('', src_address),
        dest_address,
        1,
        1,
        src_wallet_passowrd,
        min_confirmations=1,
    )
    rpconn.generate(1)
    raw_txid = rpconn.getrawtransaction(txid)
    raw_tx = rpconn.decoderawtransaction(raw_txid)
    values = (vout['value'] * 100000000 for vout in raw_tx['vout'] if
              vout['scriptPubKey']['addresses'].pop() == dest_address)
    assert spool_regtest.FEE in values
    assert spool_regtest.TOKEN in values
    assert (rpconn.getreceivedbyaddress(dest_address) * 100000000 ==
            spool_regtest.FEE + spool_regtest.TOKEN)


@pytest.mark.usefixtures('init_blockchain')
def test_refill_fuel(spool_regtest, rpconn):
    src_wallet_passowrd = uuid1().hex.encode('utf-8')
    src_wallet = BIP32Node.from_master_secret(src_wallet_passowrd,
                                              netcode='XTN')
    dest_wallet_passowrd = uuid1().hex.encode('utf-8')
    dest_wallet = BIP32Node.from_master_secret(dest_wallet_passowrd,
                                               netcode='XTN')
    src_address = src_wallet.bitcoin_address()
    dest_address = dest_wallet.bitcoin_address()
    rpconn.importaddress(src_address)
    rpconn.importaddress(dest_address)
    rpconn.sendtoaddress(src_address, spool_regtest.FEE/100000000)
    rpconn.sendtoaddress(src_address, spool_regtest.FEE/100000000)
    rpconn.sendtoaddress(
        src_address, spool_regtest.TOKEN/100000000)
    rpconn.generate(1)
    txid = spool_regtest.refill(
        ('', src_address),
        dest_address,
        1,
        1,
        src_wallet_passowrd,
        min_confirmations=1,
    )
    rpconn.generate(1)
    raw_txid = rpconn.getrawtransaction(txid)
    raw_tx = rpconn.decoderawtransaction(raw_txid)
    values = (vout['value'] * 100000000 for vout in raw_tx['vout'] if
              vout['scriptPubKey']['addresses'].pop() == dest_address)
    values = []
    asm = None
    for vout in raw_tx['vout']:
        try:
            addr = vout['scriptPubKey']['addresses'].pop()
        except KeyError:
            asm = vout['scriptPubKey']['asm']
        else:
            if addr == dest_address:
                values.append(vout['value'] * 100000000)

    assert spool_regtest.FEE in values
    assert spool_regtest.TOKEN in values
    assert asm.split(' ')[0] == 'OP_RETURN'
    assert asm.split(' ')[1] == '4153435249424553504f4f4c30314655454c'
    assert spool_regtest.FEE in values
    assert spool_regtest.TOKEN in values
    assert (rpconn.getreceivedbyaddress(dest_address) * 100000000 ==
            spool_regtest.FEE + spool_regtest.TOKEN)


@pytest.mark.usefixtures('init_blockchain')
def test_register_piece(rpconn,
                        federation_hd_address,
                        alice_hd_address,
                        piece_hashes,
                        spool_regtest):
    rpconn.importaddress(federation_hd_address)
    rpconn.importaddress(alice_hd_address)
    rpconn.sendtoaddress(federation_hd_address, spool_regtest.FEE/100000000)
    rpconn.sendtoaddress(federation_hd_address, spool_regtest.TOKEN/100000000)
    rpconn.sendtoaddress(federation_hd_address, spool_regtest.TOKEN/100000000)
    rpconn.sendtoaddress(federation_hd_address, spool_regtest.TOKEN/100000000)
    rpconn.generate(1)
    txid = spool_regtest.register_piece(
        ('', federation_hd_address),
        alice_hd_address,
        piece_hashes,
        b'federation-secret',
        min_confirmations=1,
    )
    assert txid


@pytest.mark.usefixtures('init_blockchain')
def test_register_edition(rpconn,
                          federation_hd_address,
                          alice_hd_address,
                          piece_hashes,
                          spool_regtest):
    rpconn.importaddress(federation_hd_address)
    rpconn.importaddress(alice_hd_address)
    rpconn.sendtoaddress(federation_hd_address, spool_regtest.FEE/100000000)
    rpconn.sendtoaddress(federation_hd_address, spool_regtest.TOKEN/100000000)
    rpconn.sendtoaddress(federation_hd_address, spool_regtest.TOKEN/100000000)
    rpconn.sendtoaddress(federation_hd_address, spool_regtest.TOKEN/100000000)
    rpconn.generate(1)
    txid = spool_regtest.register(
        ('', federation_hd_address),
        alice_hd_address,
        piece_hashes,
        b'federation-secret',
        3,
        min_confirmations=1,
    )
    assert txid
    raw_txid = rpconn.getrawtransaction(txid)
    raw_tx = rpconn.decoderawtransaction(raw_txid)
    addresses = []
    asm = None
    for vout in raw_tx['vout']:
        try:
            address = vout['scriptPubKey']['addresses'].pop()
        except KeyError:
            asm = vout['scriptPubKey']['asm']
        else:
            if vout['value'] * 100000000 == spool_regtest.TOKEN:
                addresses.append(address)
    assert alice_hd_address in addresses
    assert piece_hashes[0] in addresses
    assert piece_hashes[1] in addresses
    assert asm.split(' ')[0] == 'OP_RETURN'
    assert codecs.decode(
        asm.split(' ')[1], 'hex') == b'ASCRIBESPOOL01REGISTER3'


@pytest.mark.usefixtures('init_blockchain')
def test_consigned_registration(rpconn,
                                federation_hd_address,
                                alice_hd_address,
                                piece_hashes,
                                spool_regtest):
    rpconn.importaddress(federation_hd_address)
    rpconn.importaddress(alice_hd_address)
    rpconn.sendtoaddress(federation_hd_address, spool_regtest.FEE/100000000)
    rpconn.sendtoaddress(federation_hd_address, spool_regtest.TOKEN/100000000)
    rpconn.sendtoaddress(federation_hd_address, spool_regtest.TOKEN/100000000)
    rpconn.sendtoaddress(federation_hd_address, spool_regtest.TOKEN/100000000)
    rpconn.generate(1)
    txid = spool_regtest.consigned_registration(
        ('', federation_hd_address),
        alice_hd_address,
        piece_hashes,
        b'federation-secret',
        min_confirmations=1,
    )
    assert txid
    raw_txid = rpconn.getrawtransaction(txid)
    raw_tx = rpconn.decoderawtransaction(raw_txid)
    addresses = []
    asm = None
    for vout in raw_tx['vout']:
        try:
            address = vout['scriptPubKey']['addresses'].pop()
        except KeyError:
            asm = vout['scriptPubKey']['asm']
        else:
            if vout['value'] * 100000000 == spool_regtest.TOKEN:
                addresses.append(address)
    assert alice_hd_address in addresses
    assert piece_hashes[0] in addresses
    assert piece_hashes[1] in addresses
    assert asm.split(' ')[0] == 'OP_RETURN'
    assert codecs.decode(
        asm.split(' ')[1], 'hex') == b'ASCRIBESPOOL01CONSIGNEDREGISTRATION'


@pytest.mark.usefixtures('init_blockchain')
def test_editions(rpconn,
                  federation_hd_address,
                  alice_hd_address,
                  piece_hashes,
                  spool_regtest):
    rpconn.importaddress(federation_hd_address)
    rpconn.importaddress(alice_hd_address)
    rpconn.sendtoaddress(federation_hd_address, spool_regtest.FEE/100000000)
    rpconn.sendtoaddress(federation_hd_address, spool_regtest.TOKEN/100000000)
    rpconn.sendtoaddress(federation_hd_address, spool_regtest.TOKEN/100000000)
    rpconn.sendtoaddress(federation_hd_address, spool_regtest.TOKEN/100000000)
    rpconn.generate(1)
    txid = spool_regtest.editions(
        ('', federation_hd_address),
        alice_hd_address,
        piece_hashes,
        b'federation-secret',
        7,
        min_confirmations=1,
    )
    assert txid
    raw_txid = rpconn.getrawtransaction(txid)
    raw_tx = rpconn.decoderawtransaction(raw_txid)
    addresses = []
    asm = None
    for vout in raw_tx['vout']:
        try:
            address = vout['scriptPubKey']['addresses'].pop()
        except KeyError:
            asm = vout['scriptPubKey']['asm']
        else:
            if vout['value'] * 100000000 == spool_regtest.TOKEN:
                addresses.append(address)
    assert alice_hd_address in addresses
    assert piece_hashes[0] in addresses
    assert piece_hashes[1] in addresses
    assert asm.split(' ')[0] == 'OP_RETURN'
    assert codecs.decode(
        asm.split(' ')[1], 'hex') == b'ASCRIBESPOOL01EDITIONS7'


@pytest.mark.usefixtures('init_blockchain')
def test_transfer(rpconn,
                  federation_hd_address,
                  alice_hd_address,
                  piece_hashes,
                  spool_regtest):
    rpconn.importaddress(federation_hd_address)
    rpconn.importaddress(alice_hd_address)
    rpconn.sendtoaddress(federation_hd_address, spool_regtest.FEE/100000000)
    rpconn.sendtoaddress(federation_hd_address, spool_regtest.TOKEN/100000000)
    rpconn.sendtoaddress(federation_hd_address, spool_regtest.TOKEN/100000000)
    rpconn.sendtoaddress(federation_hd_address, spool_regtest.TOKEN/100000000)
    rpconn.generate(1)
    txid = spool_regtest.transfer(
        ('', federation_hd_address),
        alice_hd_address,
        piece_hashes,
        b'federation-secret',
        5,
        min_confirmations=1,
    )
    assert txid
    raw_txid = rpconn.getrawtransaction(txid)
    raw_tx = rpconn.decoderawtransaction(raw_txid)
    addresses = []
    asm = None
    for vout in raw_tx['vout']:
        try:
            address = vout['scriptPubKey']['addresses'].pop()
        except KeyError:
            asm = vout['scriptPubKey']['asm']
        else:
            if vout['value'] * 100000000 == spool_regtest.TOKEN:
                addresses.append(address)
    assert alice_hd_address in addresses
    assert piece_hashes[0] in addresses
    assert asm.split(' ')[0] == 'OP_RETURN'
    assert codecs.decode(
        asm.split(' ')[1], 'hex') == b'ASCRIBESPOOL01TRANSFER5'


@pytest.mark.usefixtures('init_blockchain')
def test_consign(rpconn,
                 federation_hd_address,
                 alice_hd_address,
                 piece_hashes,
                 spool_regtest):
    rpconn.importaddress(federation_hd_address)
    rpconn.importaddress(alice_hd_address)
    rpconn.sendtoaddress(federation_hd_address, spool_regtest.FEE/100000000)
    rpconn.sendtoaddress(federation_hd_address, spool_regtest.TOKEN/100000000)
    rpconn.sendtoaddress(federation_hd_address, spool_regtest.TOKEN/100000000)
    rpconn.sendtoaddress(federation_hd_address, spool_regtest.TOKEN/100000000)
    rpconn.generate(1)
    txid = spool_regtest.consign(
        ('', federation_hd_address),
        alice_hd_address,
        piece_hashes,
        b'federation-secret',
        4,
        min_confirmations=1,
    )
    assert txid
    raw_txid = rpconn.getrawtransaction(txid)
    raw_tx = rpconn.decoderawtransaction(raw_txid)
    addresses = []
    asm = None
    for vout in raw_tx['vout']:
        try:
            address = vout['scriptPubKey']['addresses'].pop()
        except KeyError:
            asm = vout['scriptPubKey']['asm']
        else:
            if vout['value'] * 100000000 == spool_regtest.TOKEN:
                addresses.append(address)
    assert alice_hd_address in addresses
    assert piece_hashes[0] in addresses
    assert asm.split(' ')[0] == 'OP_RETURN'
    assert codecs.decode(asm.split(' ')[1], 'hex') == b'ASCRIBESPOOL01CONSIGN4'


@pytest.mark.usefixtures('init_blockchain')
def test_unconsign(rpconn,
                   federation_hd_address,
                   alice_hd_address,
                   piece_hashes,
                   spool_regtest):
    rpconn.importaddress(federation_hd_address)
    rpconn.importaddress(alice_hd_address)
    rpconn.sendtoaddress(federation_hd_address, spool_regtest.FEE/100000000)
    rpconn.sendtoaddress(federation_hd_address, spool_regtest.TOKEN/100000000)
    rpconn.sendtoaddress(federation_hd_address, spool_regtest.TOKEN/100000000)
    rpconn.sendtoaddress(federation_hd_address, spool_regtest.TOKEN/100000000)
    rpconn.generate(1)
    txid = spool_regtest.unconsign(
        ('', federation_hd_address),
        alice_hd_address,
        piece_hashes,
        b'federation-secret',
        8,
        min_confirmations=1,
    )
    assert txid
    raw_txid = rpconn.getrawtransaction(txid)
    raw_tx = rpconn.decoderawtransaction(raw_txid)
    addresses = []
    asm = None
    for vout in raw_tx['vout']:
        try:
            address = vout['scriptPubKey']['addresses'].pop()
        except KeyError:
            asm = vout['scriptPubKey']['asm']
        else:
            if vout['value'] * 100000000 == spool_regtest.TOKEN:
                addresses.append(address)
    assert alice_hd_address in addresses
    assert piece_hashes[0] in addresses
    assert asm.split(' ')[0] == 'OP_RETURN'
    assert codecs.decode(
        asm.split(' ')[1], 'hex') == b'ASCRIBESPOOL01UNCONSIGN8'


@pytest.mark.usefixtures('init_blockchain')
def test_loan(rpconn, federation_hd_address,
              alice_hd_address, piece_hashes, spool_regtest):
    rpconn.importaddress(federation_hd_address)
    rpconn.importaddress(alice_hd_address)
    rpconn.sendtoaddress(federation_hd_address, spool_regtest.FEE/100000000)
    rpconn.sendtoaddress(federation_hd_address, spool_regtest.TOKEN/100000000)
    rpconn.sendtoaddress(federation_hd_address, spool_regtest.TOKEN/100000000)
    rpconn.sendtoaddress(federation_hd_address, spool_regtest.TOKEN/100000000)
    rpconn.generate(1)
    txid = spool_regtest.loan(
        ('', federation_hd_address),
        alice_hd_address,
        piece_hashes,
        b'federation-secret',
        2,
        '160613',
        '160701',
        min_confirmations=1,
    )
    assert txid
    raw_txid = rpconn.getrawtransaction(txid)
    raw_tx = rpconn.decoderawtransaction(raw_txid)
    addresses = []
    asm = None
    for vout in raw_tx['vout']:
        try:
            address = vout['scriptPubKey']['addresses'].pop()
        except KeyError:
            asm = vout['scriptPubKey']['asm']
        else:
            if vout['value'] * 100000000 == spool_regtest.TOKEN:
                addresses.append(address)
    assert alice_hd_address in addresses
    assert piece_hashes[0] in addresses
    assert asm.split(' ')[0] == 'OP_RETURN'
    assert codecs.decode(
        asm.split(' ')[1], 'hex') == b'ASCRIBESPOOL01LOAN2/160613160701'


@pytest.mark.usefixtures('init_blockchain')
def test_migrate(rpconn,
                 federation_hd_address,
                 alice_hd_address,
                 piece_hashes,
                 spool_regtest):
    rpconn.importaddress(federation_hd_address)
    rpconn.importaddress(alice_hd_address)
    new_address = rpconn.getnewaddress()
    rpconn.sendtoaddress(federation_hd_address, spool_regtest.FEE/100000000)
    rpconn.sendtoaddress(federation_hd_address, spool_regtest.TOKEN/100000000)
    rpconn.sendtoaddress(federation_hd_address, spool_regtest.TOKEN/100000000)
    rpconn.sendtoaddress(federation_hd_address, spool_regtest.TOKEN/100000000)
    rpconn.generate(1)
    txid = spool_regtest.migrate(
        ('', federation_hd_address),
        alice_hd_address,
        new_address,
        piece_hashes,
        b'federation-secret',
        9,
        min_confirmations=1,
    )
    assert txid
    raw_txid = rpconn.getrawtransaction(txid)
    raw_tx = rpconn.decoderawtransaction(raw_txid)
    addresses = []
    asm = None
    for vout in raw_tx['vout']:
        try:
            address = vout['scriptPubKey']['addresses'].pop()
        except KeyError:
            asm = vout['scriptPubKey']['asm']
        else:
            if vout['value'] * 100000000 == spool_regtest.TOKEN:
                addresses.append(address)
    assert alice_hd_address in addresses
    assert new_address in addresses
    assert piece_hashes[0] in addresses
    assert asm.split(' ')[0] == 'OP_RETURN'
    assert codecs.decode(asm.split(' ')[1], 'hex') == b'ASCRIBESPOOL01MIGRATE9'
