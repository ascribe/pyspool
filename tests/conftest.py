# -*- coding: utf-8 -*-

from __future__ import division, unicode_literals
from builtins import range

import os
from uuid import uuid1

import pytest

from bitcoinrpc.authproxy import AuthServiceProxy
from pycoin.key.BIP32Node import BIP32Node
from transactions import Transactions


def reload_address(address, rpconn, times=1):
    """
    Sends necessary satoshis for a Spool transaction.

    Args:
        address (str): receiving bitcoin address
        rpconn (AuthServiceProxy): JSON-RPC connection
            (:class:`AuthServiceProxy` instance) to bitcoin regtest

    """
    from spool import Spool
    for _ in range(times):
        rpconn.sendtoaddress(address, Spool.FEE/100000000)
        rpconn.sendtoaddress(address, Spool.TOKEN/100000000)
        rpconn.sendtoaddress(address, Spool.TOKEN/100000000)
        rpconn.sendtoaddress(address, Spool.TOKEN/100000000)
    rpconn.generate(1)


@pytest.fixture
def alice_hd_wallet():
    return BIP32Node.from_master_secret(b'alice-secret', netcode='XTN')


@pytest.fixture
def alice_hd_address(alice_hd_wallet):
    return alice_hd_wallet.bitcoin_address()


@pytest.fixture
def alice(alice_hd_address, rpconn, request):
    rpconn.importaddress(alice_hd_address)
    rpconn.setaccount(alice_hd_address, request.fixturename)
    return alice_hd_address


@pytest.fixture
def bob_hd_wallet():
    return BIP32Node.from_master_secret(b'bob-secret', netcode='XTN')


@pytest.fixture
def bob_hd_address(bob_hd_wallet):
    return bob_hd_wallet.bitcoin_address()


@pytest.fixture
def bob(bob_hd_address, rpconn, request):
    rpconn.importaddress(bob_hd_address)
    rpconn.setaccount(bob_hd_address, request.fixturename)
    return bob_hd_address


@pytest.fixture
def carol_hd_wallet():
    return BIP32Node.from_master_secret(b'carol-secret', netcode='XTN')


@pytest.fixture
def carol_hd_address(carol_hd_wallet):
    return carol_hd_wallet.bitcoin_address()


@pytest.fixture
def carol(carol_hd_address, rpconn, request):
    rpconn.importaddress(carol_hd_address)
    rpconn.setaccount(carol_hd_address, request.fixturename)
    return carol_hd_address


@pytest.fixture
def eve(rpconn, request):
    address = rpconn.getnewaddress()
    rpconn.setaccount(address, request.fixturename)
    return address


@pytest.fixture
def wendy(rpconn, request):
    address = rpconn.getnewaddress()
    rpconn.setaccount(address, request.fixturename)
    return address


@pytest.fixture
def federation_hd_wallet(request):
    return BIP32Node.from_master_secret(b'federation-secret', netcode='XTN')


@pytest.fixture
def federation_hd_address(federation_hd_wallet):
    return federation_hd_wallet.bitcoin_address()


@pytest.fixture
def federation(federation_hd_address, init_blockchain, rpconn):
    rpconn.importaddress(federation_hd_address)
    reload_address(federation_hd_address, rpconn)
    return federation_hd_address


@pytest.fixture
def random_bip32_wallet():
    return BIP32Node.from_master_secret(
        uuid1().hex.encode('utf-8'), netcode='XTN')


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
def transactions(rpcuser, rpcpassword, host, port):
    return Transactions(
        service='daemon',
        username=rpcuser,
        password=rpcpassword,
        host=host,
        port=port,
        testnet=True,
    )


@pytest.fixture
def spider(rpcuser, rpcpassword, host, port):
    from spool import BlockchainSpider
    return BlockchainSpider(
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


@pytest.fixture
def registered_piece_hashes(federation, alice,
                            piece_hashes, spool_regtest, rpconn):
    spool_regtest.register_piece(
        ('', federation),
        alice,
        piece_hashes,
        b'federation-secret',
        min_confirmations=1,
    )
    rpconn.generate(1)
    reload_address(federation, rpconn)
    return piece_hashes


@pytest.fixture
def registered_edition_qty_hashes(federation, alice, registered_piece_hashes,
                                  spool_regtest, rpconn):
    spool_regtest.editions(
        ('', federation),
        alice,
        registered_piece_hashes,
        b'federation-secret',
        3,
        min_confirmations=1,
    )
    rpconn.generate(1)
    reload_address(federation, rpconn)
    return registered_piece_hashes


@pytest.fixture
def registered_edition_one_hashes(federation, alice, spool_regtest, rpconn,
                                  registered_edition_qty_hashes):
    spool_regtest.register(
        ('', federation),
        alice,
        registered_edition_qty_hashes,
        b'federation-secret',
        1,
        min_confirmations=1,
    )
    rpconn.generate(1)
    reload_address(federation, rpconn)
    return registered_edition_qty_hashes


@pytest.fixture
def registered_edition_two_hashes(federation, alice, spool_regtest, rpconn,
                                  registered_edition_qty_hashes):
    spool_regtest.register(
        ('', federation),
        alice,
        registered_edition_qty_hashes,
        b'federation-secret',
        2,
        min_confirmations=1,
    )
    rpconn.generate(1)
    reload_address(federation, rpconn)
    return registered_edition_qty_hashes


@pytest.fixture
def transferred_edition_two_hashes(federation, alice, bob, spool_regtest,
                                   registered_edition_two_hashes, rpconn):
    reload_address(alice, rpconn)
    spool_regtest.transfer(
        ('', alice),
        bob,
        registered_edition_two_hashes,
        b'alice-secret',
        2,
        min_confirmations=1,
    )
    rpconn.generate(1)
    return registered_edition_two_hashes


@pytest.fixture
def loan_start():
    return '171017'


@pytest.fixture
def loan_end():
    return '181018'


@pytest.fixture
def loaned_piece_hashes(federation, alice, carol, spool_regtest,
                        registered_piece_hashes, rpconn,
                        loan_start, loan_end):
    reload_address(alice, rpconn)
    spool_regtest.loan(
        ('', alice),
        carol,
        registered_piece_hashes,
        b'alice-secret',
        0,
        loan_start,
        loan_end,
        min_confirmations=1,
    )
    rpconn.generate(1)
    return registered_piece_hashes


@pytest.fixture
def loaned_edition_one_hashes(federation, alice, carol, spool_regtest,
                              registered_edition_one_hashes, rpconn,
                              loan_start, loan_end):
    reload_address(alice, rpconn)
    spool_regtest.loan(
        ('', alice),
        carol,
        registered_edition_one_hashes,
        b'alice-secret',
        1,
        loan_start,
        loan_end,
        min_confirmations=1,
    )
    rpconn.generate(1)
    return registered_edition_one_hashes


@pytest.fixture
def loaned_edition_two_hashes(federation, bob, carol, spool_regtest,
                              transferred_edition_two_hashes, rpconn,
                              loan_start, loan_end):
    reload_address(bob, rpconn)
    spool_regtest.loan(
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
    return transferred_edition_two_hashes


@pytest.fixture
def consigned_edition_one_hashes(federation, alice, carol, spool_regtest,
                                 registered_edition_one_hashes, rpconn):
    reload_address(alice, rpconn)
    spool_regtest.consign(
        ('', alice),
        carol,
        registered_edition_one_hashes,
        b'alice-secret',
        1,
        min_confirmations=1,
    )
    rpconn.generate(1)
    return registered_edition_one_hashes


@pytest.fixture
def ownership_edition_one(alice, registered_edition_one_hashes,
                          rpcuser, rpcpassword, host, port):
    from spool import Ownership
    return Ownership(
        alice,
        registered_edition_one_hashes[0],
        1,
        testnet=True,
        service='daemon',
        username=rpcuser,
        password=rpcpassword,
        host=host,
        port=port,
    )


@pytest.fixture
def squattership_edition_one(carol, registered_edition_one_hashes,
                             rpcuser, rpcpassword, host, port):
    from spool import Ownership
    return Ownership(
        carol,
        registered_edition_one_hashes[0],
        1,
        testnet=True,
        service='daemon',
        username=rpcuser,
        password=rpcpassword,
        host=host,
        port=port,
    )


@pytest.fixture
def ownership_edition_qty(alice, registered_edition_qty_hashes,
                          rpcuser, rpcpassword, host, port):
    from spool import Ownership
    return Ownership(
        alice,
        registered_edition_qty_hashes[0],
        1,
        testnet=True,
        service='daemon',
        username=rpcuser,
        password=rpcpassword,
        host=host,
        port=port,
    )


@pytest.fixture
def ownership_consigned_edition(carol, consigned_edition_one_hashes,
                                rpcuser, rpcpassword, host, port):
    from spool import Ownership
    return Ownership(
        carol,
        consigned_edition_one_hashes[0],
        1,
        testnet=True,
        service='daemon',
        username=rpcuser,
        password=rpcpassword,
        host=host,
        port=port,
    )


@pytest.fixture
def ownership_not_registered_piece(alice, piece_hashes, rpcuser,
                                   rpcpassword, host, port):
    from spool.ownership import Ownership, REGISTERED_PIECE_CODE
    return Ownership(
        alice,
        piece_hashes[0],
        REGISTERED_PIECE_CODE,
        testnet=True,
        service='daemon',
        username=rpcuser,
        password=rpcpassword,
        host=host,
        port=port,
    )
