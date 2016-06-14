# -*- coding: utf-8 -*-

from __future__ import division, unicode_literals

from uuid import uuid1
from datetime import datetime

import pytest
import pytz

from pycoin.key.BIP32Node import BIP32Node
from transactions import Transactions
from transactions.services.daemonservice import BitcoinDaemonService


def test_blockchainspider_init(rpcuser, rpcpassword, host, port):
    from spool.spoolex import BlockchainSpider
    blockchain_spider = BlockchainSpider(
        testnet=True,
        service='daemon',
        username=rpcuser,
        password=rpcpassword,
        host=host,
        port=port,
    )
    assert isinstance(blockchain_spider._t, Transactions)
    assert blockchain_spider._t.testnet is True
    assert blockchain_spider._t._service._username == rpcuser
    assert blockchain_spider._t._service._password == rpcpassword
    assert blockchain_spider._t._service._host == host
    assert blockchain_spider._t._service._port == port
    assert isinstance(blockchain_spider._t._service, BitcoinDaemonService)


@pytest.mark.usefixtures('init_blockchain')
def test_check_script(rpconn, piece_hashes, spool_regtest, transactions):
    """
    Test :staticmethod:`check_script`.

    Args;
        alice (str): bitcoin address of alice, the sender
        bob (str): bitcoin address of bob, the receiver
        rpconn (AuthServiceProxy): JSON-RPC connection
            (:class:`AuthServiceProxy` instance) to bitcoin regtest
        transactions (Transactions): :class:`Transactions` instance to
            communicate to the bitcoin regtest node

    """
    from spool import Spool
    from spool.spoolex import BlockchainSpider
    sender_password = uuid1().hex.encode('utf-8')
    sender_wallet = BIP32Node.from_master_secret(sender_password,
                                                 netcode='XTN')
    sender_address = sender_wallet.bitcoin_address()
    rpconn.importaddress(sender_address)
    rpconn.sendtoaddress(sender_address, Spool.FEE/100000000)
    rpconn.sendtoaddress(sender_address, Spool.TOKEN/100000000)
    rpconn.sendtoaddress(sender_address, Spool.TOKEN/100000000)
    rpconn.sendtoaddress(sender_address, Spool.TOKEN/100000000)
    rpconn.generate(1)
    receiver_address = rpconn.getnewaddress()
    # TODO do not rely on Spool
    txid = spool_regtest.transfer(
        ('', sender_address),
        receiver_address,
        piece_hashes,
        sender_password,
        5,
        min_confirmations=1,
    )
    verb = BlockchainSpider.check_script(transactions.get(txid)['vouts'])
    assert verb == 'ASCRIBESPOOL01TRANSFER5'


@pytest.mark.usefixtures('init_blockchain')
def test_check_script_with_invalid_tx(eve, wendy, rpconn, transactions):
    """
    An invalid transaction in this context is one that does not contain a
    ``vout`` for which the ``hex`` is a valid ``Spool`` verb.

    Args;
        eve (str): bitcoin address of eve, the sender
        wendy (str): bitcoin address of wendy, the receiver
        rpconn (AuthServiceProxy): JSON-RPC connection
            (:class:`AuthServiceProxy` instance) a local bitcoin regtest
        transactions (Transactions): :class:`Transactions` instance to
            communicate to the bitcoin regtest node

    """
    from spool.spoolex import BlockchainSpider
    rpconn.sendtoaddress(eve, 2)
    rpconn.generate(1)
    txid = rpconn.sendfrom('eve', wendy, 1)
    decoded_raw_transfer_tx = transactions.get(txid)
    with pytest.raises(Exception) as exc:
        BlockchainSpider.check_script(decoded_raw_transfer_tx['vouts'])
    assert exc.value.message == 'Invalid ascribe transaction'


@pytest.mark.usefixtures('init_blockchain')
def test_get_addresses(rpconn, piece_hashes, spool_regtest, transactions):
    from spool import Spool
    from spool.spoolex import BlockchainSpider
    sender_password = uuid1().hex.encode('utf-8')
    sender_wallet = BIP32Node.from_master_secret(sender_password,
                                                 netcode='XTN')
    sender_address = sender_wallet.bitcoin_address()
    rpconn.importaddress(sender_address)
    rpconn.sendtoaddress(sender_address, Spool.FEE/100000000)
    rpconn.sendtoaddress(sender_address, Spool.TOKEN/100000000)
    rpconn.sendtoaddress(sender_address, Spool.TOKEN/100000000)
    rpconn.sendtoaddress(sender_address, Spool.TOKEN/100000000)
    rpconn.generate(1)
    receiver_address = rpconn.getnewaddress()
    # TODO do not rely on Spool
    txid = spool_regtest.transfer(
        ('', sender_address),
        receiver_address,
        piece_hashes,
        sender_password,
        5,
        min_confirmations=1,
    )
    decoded_raw_transfer_tx = transactions.get(txid)
    addresses = BlockchainSpider._get_addresses(decoded_raw_transfer_tx)
    assert len(addresses) == 3
    assert addresses[0] == sender_address
    assert addresses[1] == receiver_address
    assert addresses[2] == piece_hashes[0]


@pytest.mark.usefixtures('init_blockchain')
def test_get_addresses_with_invalid_tx(eve, wendy, rpconn, transactions):
    """
    An invalid transaction in this context is one that has inputs from
    different addresses.

    Args;
        eve (str): bitcoin address of eve, the sender
        wendy (str): bitcoin address of wendy, the receiver
        rpconn (AuthServiceProxy): JSON-RPC connection
            (:class:`AuthServiceProxy` instance) a local bitcoin regtest
        transactions (Transactions): :class:`Transactions` instance to
            communicate to the bitcoin regtest node

    """
    from spool.spoolex import BlockchainSpider, InvalidTransactionError
    rpconn.sendtoaddress(eve, 1)
    rpconn.sendtoaddress(eve, 1)
    rpconn.generate(1)
    txid = rpconn.sendfrom('eve', wendy, 2)
    decoded_raw_transfer_tx = transactions.get(txid)
    with pytest.raises(InvalidTransactionError) as exc:
        BlockchainSpider._get_addresses(decoded_raw_transfer_tx)
    assert isinstance(exc.value, InvalidTransactionError)


def test_decode_op_return():
    from spool.spoolex import BlockchainSpider
    op_return_hex = '6a174153435249424553504f4f4c30315452414e5346455235'
    op_return = BlockchainSpider.decode_op_return(op_return_hex)
    assert op_return == 'ASCRIBESPOOL01TRANSFER5'


def test_get_time_utc():
    from spool.spoolex import BlockchainSpider, TIME_FORMAT
    time = '2016-06-13T17:28:03 UTC'
    timestamp = BlockchainSpider._get_time_utc(time)
    assert timestamp
    assert datetime.fromtimestamp(timestamp,
                                  tz=pytz.UTC).strftime(TIME_FORMAT) == time


def test_simplest_history(federation, alice, piece_hashes,
                          spool_regtest, spider, rpconn):
    txid = spool_regtest.register_piece(
        ('', federation),
        alice,
        piece_hashes,
        b'federation-secret',
        min_confirmations=1,
    )
    rpconn.generate(1)
    history = spider.history(piece_hashes[0])
    assert len(history) == 1
    assert '' in history
    assert len(history['']) == 1
    piece_registration_data = history[''][0]
    assert piece_registration_data['action'] == 'PIECE'
    assert piece_registration_data['edition_number'] == ''
    assert piece_registration_data['from_address'] == federation
    assert piece_registration_data['number_editions'] == 0
    assert piece_registration_data['piece_address'] == piece_hashes[0]
    assert piece_registration_data['timestamp_utc']
    assert piece_registration_data['to_address'] == alice
    assert piece_registration_data['txid'] == txid
    assert piece_registration_data['verb'] == 'ASCRIBESPOOL01PIECE'


def test_register_editions_qty_history(federation,
                                       alice,
                                       registered_piece_hashes,
                                       spool_regtest,
                                       spider,
                                       rpconn):
    txid = spool_regtest.editions(
        ('', federation),
        alice,
        registered_piece_hashes,
        b'federation-secret',
        3,
        min_confirmations=1,
    )
    rpconn.generate(1)
    history = spider.history(registered_piece_hashes[0])
    assert len(history) == 2
    assert '' in history
    assert 0 in history
    assert len(history['']) == 1
    assert len(history[0]) == 1
    editions_data = history[0][0]
    assert editions_data['action'] == 'EDITIONS'
    assert editions_data['edition_number'] == 0
    assert editions_data['from_address'] == federation
    assert editions_data['number_editions'] == 3
    assert editions_data['piece_address'] == registered_piece_hashes[0]
    assert editions_data['timestamp_utc']
    assert editions_data['to_address'] == alice
    assert editions_data['txid'] == txid
    assert editions_data['verb'] == 'ASCRIBESPOOL01EDITIONS3'


def test_register_edition_history(federation, alice, spool_regtest, spider,
                                  registered_edition_qty_hashes, rpconn):
    edition_number = 2
    piece_hash = registered_edition_qty_hashes[0]
    txid = spool_regtest.register(
        ('', federation),
        alice,
        registered_edition_qty_hashes,
        b'federation-secret',
        edition_number,
        min_confirmations=1,
    )
    rpconn.generate(1)
    history = spider.history(piece_hash)
    assert len(history) == 3
    assert '' in history
    assert 0 in history
    assert edition_number in history
    assert len(history['']) == 1
    assert len(history[0]) == 1
    assert len(history[edition_number]) == 1
    edition_registration_data = history[edition_number][0]
    assert edition_registration_data['action'] == 'REGISTER'
    assert edition_registration_data['edition_number'] == edition_number
    assert edition_registration_data['from_address'] == federation
    assert edition_registration_data['number_editions'] == 3
    assert edition_registration_data['piece_address'] == piece_hash
    assert edition_registration_data['timestamp_utc']
    assert edition_registration_data['to_address'] == alice
    assert edition_registration_data['txid'] == txid
    assert edition_registration_data['verb'] == 'ASCRIBESPOOL01REGISTER2'


def test_transfer_history(federation, alice, bob, spool_regtest, spider,
                          registered_edition_two_hashes, rpconn):
    from conftest import reload_address
    reload_address(alice, rpconn)
    edition_number = 2
    piece_hash = registered_edition_two_hashes[0]
    txid = spool_regtest.transfer(
        ('', alice),
        bob,
        registered_edition_two_hashes,
        b'alice-secret',
        edition_number,
        min_confirmations=1,
    )
    rpconn.generate(1)
    history = spider.history(piece_hash)
    assert len(history) == 3
    assert '' in history
    assert 0 in history
    assert edition_number in history
    assert len(history['']) == 1
    assert len(history[0]) == 1
    assert len(history[edition_number]) == 2
    transfer_data = history[edition_number][1]
    assert transfer_data['action'] == 'TRANSFER'
    assert transfer_data['edition_number'] == edition_number
    assert transfer_data['from_address'] == alice
    assert transfer_data['number_editions'] == 3
    assert transfer_data['piece_address'] == piece_hash
    assert transfer_data['timestamp_utc']
    assert transfer_data['to_address'] == bob
    assert transfer_data['txid'] == txid
    assert transfer_data['verb'] == 'ASCRIBESPOOL01TRANSFER2'


def test_loan_history(federation, bob, carol, spool_regtest, spider,
                      transferred_edition_two_hashes, rpconn):
    from conftest import reload_address
    edition_number = 2
    loan_start, loan_end = '171017', '181018'
    piece_hash = transferred_edition_two_hashes[0]
    reload_address(bob, rpconn)
    txid = spool_regtest.loan(
        ('', bob),
        carol,
        transferred_edition_two_hashes,
        b'bob-secret',
        2,
        loan_start,
        loan_end,
        min_confirmations=1,
    )
    rpconn.generate(1)
    history = spider.history(piece_hash)
    assert len(history) == 3
    assert '' in history
    assert 0 in history
    assert edition_number in history
    assert len(history['']) == 1
    assert len(history[0]) == 1
    assert len(history[edition_number]) == 3
    loan_data = history[edition_number][2]
    assert loan_data['action'] == 'LOAN'
    assert loan_data['edition_number'] == edition_number
    assert loan_data['from_address'] == bob
    assert loan_data['number_editions'] == 3
    assert loan_data['piece_address'] == piece_hash
    assert loan_data['timestamp_utc']
    assert loan_data['to_address'] == carol
    assert loan_data['txid'] == txid
    assert loan_data['verb'] == 'ASCRIBESPOOL01LOAN2/171017181018'


def test_chain(loaned_edition_two_hashes, spider):
    from spool import BlockchainSpider
    history = spider.history(loaned_edition_two_hashes[0])
    chain = BlockchainSpider.chain(history, 2)
    assert len(chain) == 3
    assert chain[0]['action'] == 'REGISTER'
    assert chain[1]['action'] == 'TRANSFER'
    assert chain[2]['action'] == 'LOAN'
    assert chain[0]['edition_number'] == 2
    assert chain[1]['edition_number'] == 2
    assert chain[2]['edition_number'] == 2


def test_strip_loan(loaned_edition_two_hashes, spider):
    from spool import BlockchainSpider
    history = spider.history(loaned_edition_two_hashes[0])
    chain = BlockchainSpider.chain(history, 2)
    assert len(chain) == 3
    assert 'LOAN' in (tx['action'] for tx in chain)
    chain = BlockchainSpider.strip_loan(chain)
    assert len(chain) == 2
    assert 'LOAN' not in (tx['action'] for tx in chain)


def test_pprint(transferred_edition_two_hashes, spider):
    from spool import BlockchainSpider
    history = spider.history(transferred_edition_two_hashes[0])
    BlockchainSpider.pprint(history)
