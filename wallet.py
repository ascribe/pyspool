"""
Wallet related methods
"""
from pycoin.key.BIP32Node import BIP32Node
from datetime import datetime


class Wallet(object):

    """Wallet"""

    def __init__(self, password, testnet=False):
        """Create a BIP32 wallet.

        :password: master secret for the wallet

        """
        netcode = 'XTN' if testnet else 'BTC'
        self.wallet = BIP32Node.from_master_secret(password, netcode=netcode)
        self.root_address = ('', self.wallet.address())

    def address_from_path(self, path=None):
        """TODO: Docstring for create_new_address.

        :account: TODO
        :returns: new_address

        """
        path = path if path else self._unique_hierarchical_string()
        return path, self.wallet.subkey_for_path(path).address()

    def _unique_hierarchical_string(self):
        """@return -- e.g. '2014/2/23/15/26/8/9877978'
        The last part (microsecond) is needed to avoid duplicates in rapid-fire transactions e.g. >1 edition"""
        t = datetime.now()
        return '%s/%s/%s/%s/%s/%s/%s' % (t.year, t.month, t.day, t.hour, t.minute, t.second, t.microsecond)