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
            (:class:`AuthServiceProxy` instance) a local bitcoin regtest
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
def test_check_script_with_invalid_tx(alice, bob, rpconn, transactions):
    """
    An invalid transaction in this context is one that does not contain a
    ``vout`` for which the ``hex`` is a valid ``Spool`` verb.

    Args;
        alice (str): bitcoin address of alice, the sender
        bob (str): bitcoin address of bob, the receiver
        rpconn (AuthServiceProxy): JSON-RPC connection
            (:class:`AuthServiceProxy` instance) a local bitcoin regtest
        transactions (Transactions): :class:`Transactions` instance to
            communicate to the bitcoin regtest node

    """
    from spool.spoolex import BlockchainSpider
    rpconn.sendtoaddress(alice, 2)
    rpconn.generate(1)
    txid = rpconn.sendfrom('alice', bob, 1)
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
def test_get_addresses_with_invalid_tx(alice, bob, rpconn, transactions):
    """
    An invalid transaction in this context is one that has inputs from
    different addresses.

    Args;
        alice (str): bitcoin address of alice, the sender
        bob (str): bitcoin address of bob, the receiver
        rpconn (AuthServiceProxy): JSON-RPC connection
            (:class:`AuthServiceProxy` instance) a local bitcoin regtest
        transactions (Transactions): :class:`Transactions` instance to
            communicate to the bitcoin regtest node

    """
    from spool.spoolex import BlockchainSpider, InvalidTransactionError
    rpconn.sendtoaddress(alice, 1)
    rpconn.sendtoaddress(alice, 1)
    rpconn.generate(1)
    txid = rpconn.sendfrom('alice', bob, 2)
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
