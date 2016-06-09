# -*- coding: utf-8 -*-

from __future__ import unicode_literals

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
