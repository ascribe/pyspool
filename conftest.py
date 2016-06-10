# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os

import pytest

from bitcoinrpc.authproxy import AuthServiceProxy


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
