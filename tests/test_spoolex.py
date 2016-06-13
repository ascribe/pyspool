# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from datetime import datetime

import pytz

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
