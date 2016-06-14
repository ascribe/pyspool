import binascii
import calendar

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
TIME_FORMAT = '%Y-%m-%dT%H:%M:%S %Z'


class InvalidTransactionError(Exception):

    """
    To be raised when a malformed/invalid transaction is found.
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class BlockchainSpider(object):
    """
    Spool blockain explorer. Retrieves from the blockchain the chain of ownership of a hash created
    with the SPOOL protocol
    """

    def __init__(self, testnet=False, service='blockr', username='', password='', host='', port=''):
        """

        :param testnet: testnet flag. Defaults to False
        :return: An instance of the BlockainSpider
        """
        self._t = Transactions(service=service, testnet=testnet, username=username,
                               password=password, host=host, port=port)

    def history(self, hash):
        """
        Retrieve the ownership tree of all editions of a piece given the hash.

        Args:
            hash (str): Hash of the file to check. Can be created with the
                :class:`File` class

        Returns:
            ownsership tree of all editions of a piece

        .. note:: For now we only support searching the blockchain by
            the piece hash.

        """
        txs = self._t.get(hash, max_transactions=10000)['transactions']
        tree = defaultdict(list)
        number_editions = 0

        for tx in txs:
            _tx = self._t.get(tx['txid'])
            txid = _tx['txid']
            verb_str = BlockchainSpider.check_script(_tx['vouts'])
            verb = Spoolverb.from_verb(verb_str)
            from_address, to_address, piece_address = BlockchainSpider._get_addresses(_tx)
            timestamp_utc = _tx['time']
            action = verb.action

            edition_number = 0
            if action != 'EDITIONS':
                edition_number = verb.edition_number
            else:
                number_editions = verb.num_editions

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
        """

        :param tree: Tree history of all editions of a piece
        :param edition_number: The edition number to check for
        :return: The chain of ownsership of a particular edition of the piece ordered by time
        """
        # return the chain for an edition_number sorted by the timestamp
        return sorted(tree.get(edition_number, []), key=lambda d: d['timestamp_utc'])

    @staticmethod
    def strip_loan(chain):
        """
        Returns the chain without loan. This way we can look at the last transaction
        to establish ownership

        :param chain: chain for a particular edition
        :return: chain with loan transactions striped from the end of the chain
        """
        while chain[-1]['action'] == 'LOAN':
            chain.pop()

        return chain

    @staticmethod
    def pprint(tree):
        """
        Utility function to pretty print the history tree of a piece
        :param tree: History tree of a piece
        :return: None
        """
        p = PrettyPrinter(indent=2)
        p.pprint(tree)

    @staticmethod
    def decode_op_return(op_return_hex):
        """
        Decodes the op_return hex representation into a string

        Args:
            op_return_hex (str): hex representation of the op_return

        Returns:
            str: tring representation of the op_return

        """
        return binascii.unhexlify(op_return_hex[4:])

    @staticmethod
    def check_script(vouts):
        """
        Looks into the vouts list of a transaction and returns the
        ``op_return`` if one exists.

        Args;
            vouts (List[dict]): list of outputs of a transaction

        Returns:
            str: string representation of the ``op_return``

        """
        for vout in [v for v in vouts[::-1] if v['hex'].startswith('6a')]:
            verb = BlockchainSpider.decode_op_return(vout['hex'])
            action = Spoolverb.from_verb(verb).action
            if action in Spoolverb.supported_actions:
                return verb
        raise Exception("Invalid ascribe transaction")

    @staticmethod
    def _get_addresses(tx):
        """
        Checks for the from, to, and piece address of a SPOOL transaction.

        Args:
            tx (dict): transaction payload, as returned by
                ``transactions.Transactions.get()``

        .. note:: Formats as returned by JSON-RPC API ``decoderawtransaction``
            have yet to be supported.

        Returns:
            Tuple([str]): sender, receiver, and piece addresses

        """
        from_address = set([vin['address'] for vin in tx['vins']])
        if len(from_address) != 1:
            raise InvalidTransactionError("Transaction should have inputs " \
                                          "from only one address {}".format(from_address))

        # order vouts. discard the last vout since it's the op_return
        vouts = sorted(tx['vouts'], key=lambda d: d['n'])[:-1]
        piece_address = vouts[0]['address']
        to_address = vouts[-1]['address']
        from_address = from_address.pop()

        return from_address, to_address, piece_address

    @staticmethod
    def _get_time_utc(time_utc_str):
        """
        Convert a string representation of the time (as returned by
        blockr.io api) into unix timestamp.

        Args:
            time_utc_str (str): string representation of the time, with the
                format: `'%Y-%m-%dT%H:%M:%S %Z'`

        Returns:
            int: unix timestamp

        """
        dt = datetime.strptime(time_utc_str, TIME_FORMAT)
        return int(calendar.timegm(dt.utctimetuple()))
