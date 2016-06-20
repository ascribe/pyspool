# -*- coding: utf-8 -*-
"""
Wallet related methods
"""
from __future__ import unicode_literals

from builtins import object, str
from datetime import datetime

from pycoin.key.BIP32Node import BIP32Node


class Wallet(object):
    """
    Represents a BIP32 wallet.

    Attributes:
        wallet (BIP32Node): :class:`BIP32NOde` instance.
        root_address (Tuple[str]): Root address of the HD Wallet.

    """

    def __init__(self, password, testnet=False):
        """
        Initializes a BIP32 wallet.

        Addresses returned by the wallet are of the form ``(path, address)``.

        Args:
            password (bytes): Master secret for the wallet. The password can
                also be passed as a string (``str``).
            testnet (bool): Wwether to use the bitcoin testnet or mainnet.
                Defaults to ``False``.

        """
        netcode = 'XTN' if testnet else 'BTC'
        if isinstance(password, str):
            password = password.encode()
        self.wallet = BIP32Node.from_master_secret(password, netcode=netcode)
        self.root_address = ('', self.wallet.address())

    def address_from_path(self, path=None):
        """
        Args:
            path (str): Path for the HD wallet. If path is ``None`` it
                will generate a unique path based on time.

        Returns:
            A ``tuple`` with the path and leaf address.

        """
        path = path if path else self._unique_hierarchical_string()
        return path, self.wallet.subkey_for_path(path).address()

    def _unique_hierarchical_string(self):
        """
        Returns:
            str: a representation of time such as::

                '2014/2/23/15/26/8/9877978'

        The last part (microsecond) is needed to avoid duplicates in
        rapid-fire transactions e.g. ``> 1`` edition.

        """
        t = datetime.now()
        return '%s/%s/%s/%s/%s/%s/%s' % (t.year, t.month, t.day, t.hour,
                                         t.minute, t.second, t.microsecond)
