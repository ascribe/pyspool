"""
Util functions
"""
import time

from functools import wraps
from ownership import Ownership, OwnershipError
from transactions import Transactions
from spoolex import BlockchainSpider

# number of seconds between transaction confirmed checks.
# only needed for when calling a method with sync=True
TIMEOUT = 10
MAX_TIMEOUT = 40   # max timeout in which the exponential backoff will stop


def dispatch(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        sync = kwargs.get('sync', False)
        ownsership = kwargs.get('ownership', False)
        name = f.__name__
        testnet = args[0].testnet
        t = args[0]._t
        from_address = args[1][1]
        to_address = args[2]
        password = args[4]      # TODO remove, as it is not used
        # a piece has no edition number
        if name not in ['register_piece', 'consigned_registration']:
            edition_number = args[5]
        hash = ''
        if name not in ['refill', 'refill_main_wallet']:
            hash = args[3][0]

        # check ownership
        if ownsership:
            if name == 'register' and edition_number == 0:
                ow = Ownership(to_address, hash, edition_number, testnet=testnet)
                if not ow.can_register_master:
                    raise OwnershipError(ow.reason)
            elif name == 'register' and edition_number != 0:
                ow = Ownership(to_address, hash, edition_number, testnet=testnet)
                if not ow.can_register:
                    raise OwnershipError(ow.reason)
            elif name == 'editions':
                ow = Ownership(to_address, hash, edition_number, testnet=testnet)
                if not ow.can_editions:
                    raise OwnershipError(ow.reason)
            elif name == 'transfer' or name == 'consign' or name == 'loan':
                ow = Ownership(from_address, hash, edition_number, testnet=testnet)
                if not ow.can_transfer:
                    raise OwnershipError(ow.reason)
            elif name == 'unconsign':
                ow = Ownership(from_address, hash, edition_number, testnet=testnet)
                if not ow.can_unconsign:
                    raise OwnershipError(ow.reason)

                # check the to address
                chain = BlockchainSpider.chain(ow._tree, edition_number)
                chain_from_address = chain[-1]['from_address']
                if chain_from_address != to_address:
                    raise OwnershipError('You can only unconsign to {}'.format(chain_from_address))

        # do a synchronous transaction
        if sync:
            txid = f(*args, **kwargs)
            # lets give it some time for the transaction to reach the network
            confirmations = 0
            timeout = TIMEOUT
            while not confirmations:
                # lets do a simple exponential backoff. Transactions may take some time to be picked up by some
                # services
                try:
                    confirmations = t.get(txid).get('confirmations', 0)
                    timeout = TIMEOUT
                except Exception as e:
                    if e.message.find('code: 404') != -1:
                        timeout *= 2
                        if timeout > MAX_TIMEOUT:
                            raise
                    else:
                        raise
                time.sleep(timeout)
            return txid
        else:
            return f(*args, **kwargs)
    return wrapper
