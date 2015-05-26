import unittest
from ownership import Ownership

USER1_ROOT = 'n2sQHoUghWUgSM8msqdmCim8pZ635YjoCD'
USER1_LEAF = 'mmiFcUFjtVHuDFLdKKV9uydmiR9Qb34pfG'
USER2_LEAF = 'mtSLq3CCiCL7vxhNGu7BSqZpr6BBaWPbD4'
USER3_LEAF = 'mrRNSYPxrTHba8JwPxvnhpGYwPh65gPjNr'
PIECE_HASH = 'myr2VcDnPKf997sjXx6rUFc4CtFH9sxNVS'

"""
History:

USER1 -> Register master edition
USER1 -> Register number of edition
USER1 -> Register edition number 1
USER1 -> Transfer edition number 1 to USER2
USER2 -> Consign edition number 1 to USER3
USER3 -> Unconsign edition number 1 back to USER2
USER2 -> Loans edition number 1 to USER3
"""

class TestOwnership(unittest.TestCase):

    def test_ownsership(self):
        ow = Ownership(USER1_ROOT, PIECE_HASH, edition_number=1, testnet=True)

        # Master edition already on the blockchain
        self.assertFalse(ow.can_register_master)

        # Number of editions already registered
        self.assertFalse(ow.can_editions)

        # Edition 1 already registered
        self.assertFalse(ow.can_register)

        # USER1 can register editions 2 to 10
        # USER1 cannot transfer, consign, loan edition 2 to 10
        for i in range(2, 11):
            ow = Ownership(USER1_ROOT, PIECE_HASH, edition_number=i, testnet=True)
            self.assertTrue(ow.can_register)
            self.assertFalse(ow.can_transfer)
            self.assertFalse(ow.can_consign)
            self.assertFalse(ow.can_loan)

        # USER1 cannot register edition 11 because there are only 10 editions
        ow = Ownership(USER1_ROOT, PIECE_HASH, edition_number=11, testnet=True)
        self.assertFalse(ow.can_register)

        # USER2 owns edition 1
        ow = Ownership(USER2_LEAF, PIECE_HASH, edition_number=1, testnet=True)
        self.assertTrue(ow.can_transfer)
        self.assertTrue(ow.can_loan)
        self.assertTrue(ow.can_consign)

        # USER2 cannot register any edition because he does not own the master piece
        for i in range(2, 11):
            ow = Ownership(USER2_LEAF, PIECE_HASH, edition_number=i, testnet=True)
            self.assertFalse(ow.can_register)

        # USER2 loaned the piece to USER3 but USER3 cannot transfer, consign, loan
        # because he does not own the piece
        ow = Ownership(USER3_LEAF, PIECE_HASH, edition_number=1, testnet=True)
        self.assertFalse(ow.can_transfer)
        self.assertFalse(ow.can_consign)
        self.assertFalse(ow.can_loan)

