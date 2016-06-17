# -*- coding: utf-8 -*-
"""
File related methods
"""
from __future__ import unicode_literals

import hashlib
from builtins import object, str, super


from bitcoin import bin_hash160, bin_to_b58check


class ExplicitUnicodeLiteral(str):

    def __repr__(self):
        """Always return the representation with a prefixed 'u'."""
        return 'u{}'.format(super().__repr__())

urepr = ExplicitUnicodeLiteral


class File(object):

    """
    File utility class.

    Given a file name it calculates the hash of the file and the hash of the file + metadata
    """

    def __init__(self, filename, testnet=False, **kwargs):
        """
        Args:
            filename (str): Name of the file
            testnet (bool): testnet flag. Defaults to False
            **kwargs: Additional metadata to be encoded with the file. Only
                the values are used to compute the hash. Values are
                ordered using their keys, so that the computation of the
                hash is consistent. As an example, given::

                    File('filename', title='piece title', artist='artist')

                the values ``('artist', 'piece title')`` would be used in that
                order for the computation of the hash.

        Returns:
            File instance

        """
        self.testnet = testnet
        # prefix of the addresses to distinguish between mainnet and testnet
        self._magicbyte = 111 if testnet else 0
        self.file_hash, self.file_hash_metadata = self._calculate_hash(filename, **kwargs)

    @classmethod
    def from_hash(cls, hash):
        """

        :param hash: hash of the file
        :return: File instance
        """

        cls.hash = hash
        return cls

    def _calculate_hash(self, filename, **kwargs):
        """
        Calculates the hash of the file and the hash of the file + metadata
        (passed in ``kwargs``).

        Args:
            filename (str): Name of the file
            testnet (bool): testnet flag. Defaults to False
            **kwargs: Additional metadata to be encoded with the file. Only
                the values are used to compute the hash. Values are
                ordered using their keys, so that the computation of the
                hash is consistent. As an example, given::

                    File('filename', title='piece title', artist='artist')

                the values ``('artist', 'piece title')`` would be used in that
                order for the computation of the hash.

        """
        # hash to address
        with open(filename, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()

        if kwargs:
            data = str(
                [urepr(kwargs[k]) for k in sorted(kwargs)] + [file_hash])
        else:
            data = file_hash

        address_piece_with_metadata = str(
            bin_to_b58check(bin_hash160(data.encode()),
                            magicbyte=self._magicbyte)
        )
        address_piece = str(bin_to_b58check(bin_hash160(file_hash.encode()),
                                            magicbyte=self._magicbyte))
        return address_piece, address_piece_with_metadata
