import unittest

from spool import File

FILENAME = 'tests/ascribe.png'
FILE_HASH_TESTNET = 'mv5yDkR5dnjGHxietq7CH78WHk8vzsu4vH'
FILE_HASH_MAINNET = '1Fa1vhL6pmJ1WrF3BG8pTBvBRkYE6CHorQ'
FILE_HASH_METADATA_TESTNET = 'mskxntZtYiRHumod1wLFavzKBBGvpCyCNh'
FILE_HASH_METADATA_MAINNET = '1DF1VqUujgz38fL1JNMsm1mzKBgDoQgXCb'
METADATA = {'title': 'ascribe', 'artist': 'Rodolphe Marques'}


class TestFileTestnet(unittest.TestCase):

    def test_file_no_metadata(self):
        f = File(FILENAME, testnet=True)
        self.assertEqual(f.file_hash, FILE_HASH_TESTNET)
        self.assertEqual(f.file_hash_metadata, FILE_HASH_TESTNET)

    def test_file_metadata(self):
        f = File(FILENAME, testnet=True, title=METADATA['title'], artist=METADATA['artist'])
        self.assertEqual(f.file_hash_metadata, FILE_HASH_METADATA_TESTNET)
        self.assertNotEqual(f.file_hash_metadata, f.file_hash)


class TestFileMainnet(unittest.TestCase):

    def test_file_no_metadata(self):
        f = File(FILENAME)
        self.assertEqual(f.file_hash, FILE_HASH_MAINNET)
        self.assertEqual(f.file_hash_metadata, FILE_HASH_MAINNET)

    def test_file_metadata(self):
        f = File(FILENAME, title=METADATA['title'], artist=METADATA['artist'])
        self.assertEqual(f.file_hash_metadata, FILE_HASH_METADATA_MAINNET)
        self.assertNotEqual(f.file_hash_metadata, f.file_hash)