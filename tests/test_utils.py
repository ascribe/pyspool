# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import pytest


@pytest.fixture
def spool_mock():
    from spool.utils import dispatch

    class SpoolMock(object):

        def __init__(self, testnet=True):
            self.testnet = testnet
            self._t = None

        @dispatch
        def register_piece(self, *args, **kwargs):
            return 'txid'

        @dispatch
        def register(self, *args, **kwargs):
            pass

        @dispatch
        def editions(self, *args, **kwargs):
            pass

        @dispatch
        def transfer(self, *args, **kwargs):
            pass

        @dispatch
        def unconsign(self, *args, **kwargs):
            pass

    return SpoolMock()


@pytest.mark.parametrize('action', (
    'register_master', 'register', 'editions', 'transfer', 'unconsign'
))
def test_dispatch_ownership_error(action, monkeypatch, spool_mock):
    from spool.ownership import Ownership, OwnershipError
    from spool.spoolex import BlockchainSpider

    monkeypatch.setattr(BlockchainSpider, 'history', lambda s, p: None)
    monkeypatch.setattr(Ownership, 'can_{}'.format(action), False)

    with pytest.raises(OwnershipError):
        if action == 'register_master':
            edition = 0
            action = 'register'
        else:
            edition = 1
        spool_method = getattr(spool_mock, action)
        spool_method(
            (None, None), None, (None, None), None, edition, ownership=True)


def test_dispatch_unconsign_to_wrong_address(monkeypatch, spool_mock):
    from spool.ownership import Ownership, OwnershipError
    from spool.spoolex import BlockchainSpider

    @staticmethod
    def chain(x, y):
        return ({'from_address': 'chain_from_address'},)

    monkeypatch.setattr(BlockchainSpider, 'chain', chain)
    monkeypatch.setattr(BlockchainSpider, 'history', lambda s, p: None)
    monkeypatch.setattr(Ownership, 'can_unconsign', True)

    with pytest.raises(OwnershipError):
        spool_mock.unconsign(
            (None, None), 'to_address', (None, None), None, 1, ownership=True)


def test_sync(monkeypatch, spool_mock):

    class TransactionsMock(object):

        def get(self, txid):
            return {'confirmations': 1}

    setattr(spool_mock, '_t', TransactionsMock())
    monkeypatch.setattr('spool.utils.TIMEOUT', 0)
    assert spool_mock.register_piece(
        (None, None), 'to_address', (None, None), None, sync=True) == 'txid'


@pytest.mark.parametrize('exception_message', ('code: 404', 'minus_one'))
def test_sync_raises(exception_message, monkeypatch, spool_mock):

    class TransactionsMock(object):

        def get(self, txid):
            raise Exception(exception_message)

    setattr(spool_mock, '_t', TransactionsMock())

    if exception_message == 'code: 404':
        monkeypatch.setattr('spool.utils.TIMEOUT', 21)

    with pytest.raises(Exception):
        spool_mock.register_piece(
            (None, None), 'to_address', (None, None), None, sync=True)
