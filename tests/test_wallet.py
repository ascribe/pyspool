# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import unittest
from datetime import datetime

from spool import Wallet

MASTER_PASSWORD = 'MaStErPaSsWoRd'


class TestWallet(unittest.TestCase):

    def test_wallet_mainnet(self):
        wallet = Wallet(MASTER_PASSWORD)

        self.assertEqual(wallet.root_address, ('', '19XyEM554GKKAPHihuGS4J3kCbFEBvqcYz'))
        self.assertEqual(wallet.address_from_path('0/1/2/3/4/5'),
                         ('0/1/2/3/4/5', '1F2AMKyeV2DCdehRfDj3Qq1jhaZS8MSzMq'))

    def test_wallet_testnet(self):
        wallet = Wallet(MASTER_PASSWORD, testnet=True)

        self.assertEqual(wallet.root_address, ('', 'mp3vXQA3sHkZwVmLRUEotDG54aqwBVYTLd'))
        self.assertEqual(wallet.address_from_path('0/1/2/3/4/5'),
                         ('0/1/2/3/4/5', 'muY7eP4dJ3eTQmB3NnhREkE4ZaA92pgsAW'))

    def test_unique_hierarchical_path(self):
        wallet = Wallet(MASTER_PASSWORD)

        path, address = wallet.address_from_path()
        t = datetime.utcnow()
        now = '%s/%s/%s/%s/%s' % (t.year, t.month, t.day, t.hour, t.minute)
        self.assertTrue(path.find(now) != -1)
