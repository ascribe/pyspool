# -*- coding: utf-8 -*-

from __future__ import division, unicode_literals

import os
from uuid import uuid1

import pytest

from bitcoinrpc.authproxy import AuthServiceProxy
from pycoin.key.BIP32Node import BIP32Node
from transactions import Transactions


@pytest.fixture
def alice(rpconn, request):
    address = rpconn.getnewaddress()
    rpconn.setaccount(address, request.fixturename)
    return address


@pytest.fixture
def bob(rpconn, request):
    address = rpconn.getnewaddress()
    rpconn.setaccount(address, request.fixturename)
    return address


@pytest.fixture
def alice_hd_wallet():
    return BIP32Node.from_master_secret(b'alice-secret', netcode='XTN')


@pytest.fixture
def bob_hd_wallet():
    return BIP32Node.from_master_secret(b'bob-secret', netcode='XTN')


@pytest.fixture
def federation_hd_wallet(request):
    return BIP32Node.from_master_secret(b'federation-secret', netcode='XTN')


@pytest.fixture
def random_bip32_wallet():
    return BIP32Node.from_master_secret(
        uuid1().hex.encode('utf-8'), netcode='XTN')


@pytest.fixture
def alice_hd_address(alice_hd_wallet):
    return alice_hd_wallet.bitcoin_address()


@pytest.fixture
def bob_hd_address(bob_hd_wallet):
    return bob_hd_wallet.bitcoin_address()


@pytest.fixture
def federation_hd_address(federation_hd_wallet):
    return federation_hd_wallet.bitcoin_address()


@pytest.fixture
def random_bip32_address(random_bip32_wallet):
    return random_bip32_wallet.bitcoin_address()


@pytest.fixture
def host():
    return os.environ.get('BITCOIN_HOST', 'localhost')


@pytest.fixture
def port():
    return os.environ.get('BITCOIN_PORT', 18332)


@pytest.fixture
def rpcuser():
    return os.environ.get('BITCOIN_RPCUSER', 'merlin')


@pytest.fixture
def rpcpassword():
    return os.environ.get('BITCOIN_RPCPASSWORD', 'secret')


@pytest.fixture
def rpcurl(rpcuser, rpcpassword, host, port):
    return 'http://{}:{}@{}:{}'.format(rpcuser, rpcpassword, host, port)


@pytest.fixture
def rpconn(rpcurl):
    return AuthServiceProxy(rpcurl)


@pytest.fixture
def init_blockchain(rpconn):
    """
    Initialize the blockchain if needed, making sure that the balance is at
    least 50 bitcoins. The block reward only happens after 100 blocks, and for
    this reason at least 101 blocks are needed.

    """
    block_count = rpconn.getblockcount()
    if block_count < 101:
        rpconn.generate(101 - block_count)
    else:
        balance = rpconn.getbalance()
        if balance < 50:
            rpconn.generate(1)


@pytest.fixture
def spool_regtest(rpcuser, rpcpassword, host, port):
    from spool import Spool
    return Spool(
        service='daemon',
        testnet=True,
        username=rpcuser,
        password=rpcpassword,
        host=host,
        port=port,
    )


@pytest.fixture
def transactions(rpcuser, rpcpassword, host, port, rpcurl):
    return Transactions(
        service='daemon',
        username=rpcuser,
        password=rpcpassword,
        host=host,
        port=port,
        testnet=True,
    )


@pytest.fixture
def file_hash(rpconn):
    """File hash mock."""
    return rpconn.getnewaddress()


@pytest.fixture
def file_and_metadata_hash(rpconn):
    """File and metadata hash mock."""
    return rpconn.getnewaddress()


@pytest.fixture
def piece_hashes(file_hash, file_and_metadata_hash):
    """
    Pair of hashes mocking the file hash and file + metadata hash.

    Args:
        file_hash: hash of the file (mock)
        file_and_metadata_hash: hash of the file and its metadata (mock)

    Returns:
        Tuple([str]): ``file_hash`` and ``file_and_metadata_hash``

    """
    return file_hash, file_and_metadata_hash


@pytest.fixture
def decoded_raw_transfer_tx(rpconn, piece_hashes, spool_regtest, transactions):
    from spool import Spool
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
    return transactions.get(txid)
