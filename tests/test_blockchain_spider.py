import unittest

from spool import BlockchainSpider
from transactions import Transactions

PIECE_HASH = 'myr2VcDnPKf997sjXx6rUFc4CtFH9sxNVS'
OP_RETURN_HEX = '6a204153435249424553504f4f4c30314c4f414e312f313530353232313530353233'
TXID = 'fb22bbb83161f6904f1803ee1cdbed1b5836eb9ac51b102564400989780b48ea'


class TestBlockchainSpider(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        bcs = BlockchainSpider(testnet=True)
        cls.tree = bcs.history(PIECE_HASH)

    def test_history(self):
        tree = self.tree
        self.assertEqual(len(tree), 2)
        self.assertEqual(len(tree[0]), 2)
        self.assertEqual(len(tree[1]), 5)

    def test_chain(self):
        tree = self.tree

        chain0 = BlockchainSpider.chain(tree, 0)
        self.assertEqual(len(chain0), 2)

        chain1 = BlockchainSpider.chain(tree, 1)
        self.assertEqual(len(chain1), 5)

    def test_decode_op_return(self):
        decoded_op_return = BlockchainSpider.decode_op_return(OP_RETURN_HEX)
        self.assertEqual(decoded_op_return, 'ASCRIBESPOOL01LOAN1/150522150523')

    def test_check_scripts(self):
        t = Transactions(testnet=True)
        tx = t.get(TXID)
        vouts = tx['vouts']
        verb = BlockchainSpider.check_script(vouts)
        self.assertEqual(verb, 'ASCRIBESPOOL01EDITIONS10')

    def test_strip_loan(self):
        chain = BlockchainSpider.chain(self.tree, 1)
        self.assertEqual(chain[-1]['action'], 'LOAN')

        chain = BlockchainSpider.strip_loan(chain)
        self.assertEqual(len(chain), 4)
        self.assertEqual(chain[-1]['action'], 'UNCONSIGN')

    def test_data(self):
        tree = self.tree
        data = {0: tree[0]}
        self.assertDictEqual(data, {0: [{'action': 'EDITIONS',
                                         'edition_number': 0,
                                         'from_address': u'mqXz83H4LCxjf2ie8hYNsTRByvtfV43Pa7',
                                         'number_editions': 10,
                                         'piece_address': u'myr2VcDnPKf997sjXx6rUFc4CtFH9sxNVS',
                                         'timestamp_utc': 1432646255,
                                         'to_address': u'n2sQHoUghWUgSM8msqdmCim8pZ635YjoCD',
                                         'txid': u'fb22bbb83161f6904f1803ee1cdbed1b5836eb9ac51b102564400989780b48ea',
                                         'verb': 'ASCRIBESPOOL01EDITIONS10'},
                                       {'action': 'REGISTER',
                                        'edition_number': 0,
                                        'from_address': u'mqXz83H4LCxjf2ie8hYNsTRByvtfV43Pa7',
                                        'number_editions': 10,
                                        'piece_address': u'myr2VcDnPKf997sjXx6rUFc4CtFH9sxNVS',
                                        'timestamp_utc': 1432647405,
                                        'to_address': u'n2sQHoUghWUgSM8msqdmCim8pZ635YjoCD',
                                        'txid': u'02994a3ceee87be2210fa6e4a649bc0626e791f590bd8db22e7e1fd9fc66d038',
                                        'verb': 'ASCRIBESPOOL01REGISTER0'}]})