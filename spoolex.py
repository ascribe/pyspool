import binascii
import time

from collections import namedtuple, defaultdict
from exceptions import Exception
from datetime import datetime
from pprint import PrettyPrinter

from transactions import Transactions
from spoolverb import Spoolverb

SPOOLVERB = namedtuple('SPOOLVERB', ['register', 'consign', 'transfer', 'loan', 'unconsign', 'fuel'])
spoolverb = SPOOLVERB('ASCRIBESPOOL01REGISTER',
                      'ASCRIBESPOOL01CONSIGN',
                      'ASCRIBESPOOL01TRANSFER',
                      'ASCRIBESPOOL01LOAN',
                      'ASCRIBESPOOL01UNCONSIGN',
                      'ASCRIBESPOOL01FUEL')


class InvalidTransactionError(Exception):

    """
    To be raised when a malformed/invalid transaction is found.
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class BlockchainSpider(object):

    def __init__(self, testnet=False):
        self._t = Transactions(testnet=testnet)

    def history(self, hash):
        # For now we only support searching the blockchain by the piece hash
        txs = self._t.get(hash)['transactions']
        tree = defaultdict(list)
        number_editions = 0
        edition_number = 0

        for tx in txs:
            _tx = self._t.get(tx['txid'])
            txid = _tx['tx']
            verb_str = BlockchainSpider.check_script(_tx['vouts'])
            verb = Spoolverb.from_verb(verb_str)
            from_address, to_address, piece_address = BlockchainSpider._get_addresses(_tx)
            timestamp_utc = BlockchainSpider._get_time_utc(_tx['time_utc'])
            action = verb.action

            edition_number = 0
            if action != 'EDITIONS':
                edition_number = verb.edition_number
            else:
                number_editions = verb.num_editions
                num_editions_tmp = number_editions

            tree[edition_number].append({'txid': txid,
                                         'verb': verb_str,
                                         'from_address': from_address,
                                         'to_address': to_address,
                                         'piece_address': piece_address,
                                         'timestamp_utc': timestamp_utc,
                                         'action': action,
                                         'number_editions': number_editions,
                                         'edition_number': edition_number})

        # lets update the records with the number of editions of the piece since we do not know
        # this information before the EDITIONS transaction
        for edition, chain in tree.iteritems():
            [d.update({'number_editions': number_editions}) for d in chain]
        return dict(tree)

    @staticmethod
    def chain(tree, edition_number):
        # return the chain for an edition_number sorted by the timestamp
        return sorted(tree.get(edition_number, []), key=lambda d: d['timestamp_utc'])

    @staticmethod
    def pprint(tree):
        p = PrettyPrinter(indent=2)
        p.pprint(tree)

    @staticmethod
    def decode_op_return(op_return_hex):
        """
        Decodes the op_return into a string.

        op_return_hex = 0x6a + length + data

        Args:
            op_return_hex

        Returns:

        """
        return binascii.unhexlify(op_return_hex[4:])

    @staticmethod
    def check_script(vouts):
        for vout in [v for v in vouts[::-1] if v['extras']['script'].startswith('6a')]:
            verb = BlockchainSpider.decode_op_return(vout['extras']['script'])
            action = Spoolverb.get_action_from_verb(verb)
            if action in Spoolverb.supported_actions:
                return verb
        raise Exception("Invalid ascribe transaction")

    @staticmethod
    def _get_addresses(tx):
        from_address = set([vin['address'] for vin in tx['vins']])
        if len(from_address) != 1:
            raise InvalidTransactionError('Transaction should have inputs from only one address {}'.format(from_address))

        # order vouts. discard the last vout since its the op_return
        vouts = sorted(tx['vouts'], key=lambda d: d['n'])[:-1]
        piece_address = vouts[0]['address']
        to_address = vouts[-1]['address']
        from_address = from_address.pop()

        return from_address, to_address, piece_address

    @staticmethod
    def _get_time_utc(time_utc_str):
        # Receives a string representation of the time in utc
        # Returns a unix timestamp
        dt = datetime.strptime(time_utc_str, "%Y-%m-%dT%H:%M:%SZ")
        return int(time.mktime(dt.utctimetuple()))



class SpoolExplorer(object):
    _EXCLUDE_ADDRESSES = ['1JttRRdtAi6cDNM23Uq4BEU61R8kJeANJs', 'NONSTANDARD']

    def __init__(self, testnet=False, exclude_addresses=[]):
        self._t = Transactions(testnet=testnet)
        self._EXCLUDE_ADDRESSES += exclude_addresses

    def history(self, piece_address):
        """

        Args:
            address: Address of the piece

        Returns:
            list with the ownership of the piece in the form [(from_address, spoolverb, to_address), ...]

        """
        # Check if its a new address.
        # In the SPOOL protocol a piece is represented has a HD wallet in the bitcoin network
        # In order to correctly track the provenance of pieces that HD wallet should only perform
        # operations related to the spool protocol and only for one piece.
        # In order to register a piece we always need a new address.
        if not self._t.get(piece_address).get('transactions', []):
            return []

        piece_txid = self._get_tx_root(piece_address)
        history = self._follow_transaction(piece_txid, piece_address)
        return history

    def pprint(self, history):
        """

        Args:
            history: list with the ownsership history of the piece

        Returns:

        """
        for from_address, verb, to_address in history:
            print "{} -> {} -> {}".format(from_address, verb, to_address)

    def _follow_transaction(self, txid, piece_addr):
        tx = self._t.get(txid)
        print '---> ', txid

        if 'transactions' in tx:
            for _txid in [_tx['txid'] for _tx in tx['transactions'] if _tx['amount'] < 0]:
                return [] + self._follow_transaction(_txid, piece_addr)
            return []
        else:
            verb = self._check_script(tx['vouts'])
            from_address = tx['vins'][0]['address']
            to_address = [vout['address'] for vout in tx['vouts'][::-1] if vout['address'] not in self._EXCLUDE_ADDRESSES + [piece_addr]][0]

            if verb in [spoolverb.register, spoolverb.transfer, spoolverb.consign]:
                return [(from_address, verb, to_address)] + self._follow_transaction(to_address, piece_addr)
            elif verb.startswith(spoolverb.loan):
                date = verb.split(spoolverb.loan)[-1]
                date = [date[i:i+2] for i in xrange(0, len(date), 2)]
                date = '-'.join(date[:3]) + ' ' + '-'.join(date[3:])
                verb = spoolverb.loan + ' ' + date
                return [(from_address, verb, to_address)] + self._follow_transaction(to_address, piece_addr)

    def _get_tx_root(self, address):
        """
        Get the root transaction where the piece with 'hash' was registered

        Args:
            address: address of the piece to check

        Returns:
            txid: Transaction id that registered the piece

        """
        # a piece addr should only have one unspent
        # TODO: this is no longer true since all transactions have the piece addr. I need to check the first timestamp
        unspents = self._t.get(address, min_confirmations=1)['unspents']
        unspents = sorted(unspents, key=lambda d: d['confirmations'], reverse=True)
        #if len(unspents) != 1:
        #    raise InvalidTransactionError("Invalid ascribe transaction")
        txid = unspents[0]['txid']

        # lets get the transaction that created the piece and make sure its a register
        tx = self._t.get(txid)
        verb = self._check_script(tx['vouts'])
        # TODO: Remove the last check. added for debug
        if verb == spoolverb.register or verb == 'ASCRIBESPOOLREGISTER':
            return txid
        else:
            raise InvalidTransactionError('Invalid ascribe transaction')

    def _decode_op_return(self, op_return_hex):
        """
        Decodes the op_return into a string.

        op_return_hex = 0x6a + length + data

        Args:
            op_return_hex

        Returns:

        """
        return binascii.unhexlify(op_return_hex[4:])

    def _check_script(self, vouts):
        for vout in vouts:
            verb = self._decode_op_return(vout['extras']['script'])
            # TODO: Remove the last check. added for debug
            if verb in spoolverb or verb.startswith(spoolverb.loan) or verb.startswith('ASCRIBESPOOLREGISTER'):
                return verb
        raise Exception("Invalid ascribe transaction")
