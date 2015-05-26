import unittest

from spoolverb import Spoolverb


class TestSpoolverb(unittest.TestCase):

    def test_verbs(self):
        spoolverb = Spoolverb(num_editions=10, edition_num=5, loan_start='150526',
                              loan_end='150528')

        self.assertEqual(spoolverb.register, 'ASCRIBESPOOL01REGISTER5')
        self.assertEqual(spoolverb.editions, 'ASCRIBESPOOL01EDITIONS10')
        self.assertEqual(spoolverb.transfer, 'ASCRIBESPOOL01TRANSFER5')
        self.assertEqual(spoolverb.consign, 'ASCRIBESPOOL01CONSIGN5')
        self.assertEqual(spoolverb.unconsign, 'ASCRIBESPOOL01UNCONSIGN5')
        self.assertEqual(spoolverb.loan, 'ASCRIBESPOOL01LOAN5/150526150528')
        self.assertEqual(spoolverb.fuel, 'ASCRIBESPOOL01FUEL')

    def test_from_verb(self):
        spoolverb = Spoolverb.from_verb('ASCRIBESPOOL01LOAN5/150526150528')

        self.assertEqual(spoolverb.meta, 'ASCRIBESPOOL')
        self.assertEqual(spoolverb.version, '01')
        self.assertIsNone(spoolverb.num_editions)
        self.assertEqual(spoolverb.edition_number, 5)
        self.assertEqual(spoolverb.loan_start, '150526')
        self.assertEqual(spoolverb.loan_end, '150528')
        self.assertEqual(spoolverb.action, 'LOAN')

        spoolverb = Spoolverb.from_verb('ASCRIBESPOOL01EDITIONS10')
        self.assertEqual(spoolverb.num_editions, 10)