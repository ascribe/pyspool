# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from builtins import object

from .spoolex import BlockchainSpider


REGISTERED_PIECE_CODE = ''


class OwnershipError(Exception):

    """
    To be raised when an address does not have ownership of a hash

    Attributes:
        message (str): Message of the exception.

    """

    def __init__(self, message):
        """
        Args:
            message (str): Message of the exception.

        """
        self.message = message

    def __str__(self):
        return self.message


class Ownership(object):
    """
    Checks the actions that an address can make on a piece.

    Attributes:
        address (str): Bitcoin address to check ownership over
            :attr:`piece_address`.
        piece_address (str): Bitcoin address of the piece to check.
        edition_number (int): The edition number of the piece.
        testnet (bool): Bitcoin network. :const:`True` for
            ``testnet`` or :const:`False` for ``mainnet``.
        reason (str): Message indicating the reason
            for the failure of an ownership property.

    """

    def __init__(self, address, piece_address, edition_number, testnet=False,
                 service='blockr', username='', password='', host='', port=''):
        """
        Args:
            address (str): Bitcoin address to check ownership over
                ``piece_address``.
            piece_address (str): Bitcoin address of the piece to check.
            edition_number (int): The edition number of the piece.
            testnet (Optional[boo]l): Whether to use the testnet
                (:const:`True`) or the mainnet (:const:`False`).
                Defaults to :const:`False`.
            service (Optional[str]): Name of service to use to connect
                to the bitcoin network. Possible names are
                ``('blockr', 'daemon', 'regtest')``. Defaults to ``'blockr'``.
            username (Optional[str]): Username to connect to a bitcoin node
                via json-rpc based services: ``('daemon', 'regtest')``.
            password (Optional[str]): Password to connect to a bitcoin node
                via json-rpc based services: ``('daemon', 'regtest').``
            host (Optional[str]): Host of the bitcoin node to connect to
                via json-rpc based services: ``('daemon', 'regtest')``.
            port (Optional[str]): Port of the bitcoin node to connect to
                via json-rpc based services: ``('daemon', 'regtest')``.

        """
        self.address = address
        self.piece_address = piece_address
        self.edition_number = edition_number
        self.testnet = testnet
        self._bcs = BlockchainSpider(service=service, testnet=testnet, username=username,
                                     password=password, host=host, port=port)
        self._tree = self._bcs.history(piece_address)
        self.reason = ''

    @property
    def can_transfer(self):
        """
        bool: :const:`True` if :attr:`address` can transfer the edition
        :attr:`edition_number` of :attr:`piece_address` else :const:`False`.

        """
        # 1. The address needs to own the edition
        chain = BlockchainSpider.chain(self._tree, self.edition_number)

        if len(chain) == 0:
            self.reason = 'The edition number {} does not exist in the blockchain'.format(self.edition_number)
            return False

        chain = BlockchainSpider.strip_loan(chain)
        to_address = chain[-1]['to_address']
        if to_address != self.address:
            self.reason = 'Address {} does not own the edition number {}'.format(self.address, self.edition_number)
            return False

        return True

    @property
    def can_consign(self):
        """
        bool: :const:`True` if :attr:`address` can consign the edition
        :attr:`edition_number` of :attr:`piece_address` else :const:`False`.

        """
        return self.can_transfer

    @property
    def can_loan(self):
        """
        bool: :const:`True` if :attr:`address` can loan the edition
        :attr:`edition_number` of :attr:`piece_address` else :const:`False`.

        """
        return self.can_transfer

    @property
    def can_unconsign(self):
        """
        bool: :const:`True` if :attr:`address` can unconsign the edition
        :attr:`edition_number` of :attr:`piece_address` else :const:`False`.

        If the last transaction is a consignment of the edition to the user.

        """
        chain = BlockchainSpider.chain(self._tree, self.edition_number)
        if len(chain) == 0:
            self.reason = 'Master edition not yet registered'
            return False

        chain = BlockchainSpider.strip_loan(chain)
        action = chain[-1]['action']
        piece_address = chain[-1]['piece_address']
        edition_number = chain[-1]['edition_number']
        to_address = chain[-1]['to_address']

        if action != 'CONSIGN' or piece_address != self.piece_address or edition_number != self.edition_number or to_address != self.address:
            self.reason = 'Edition number {} is not consigned to {}'.format(self.edition_number, self.address)
            return False

        return True

    @property
    def can_register(self):
        """
        bool: :const:`True` if :attr:`address` can register the edition
        :attr:`edition_number` of :attr:`piece_address` else :const:`False`.

        In order to register an edition:

        1. The master piece needs to be registered.
        2. The number of editions needs to be registered.
        3. The :attr:`edition_number` should not have been registered yet.

        .. todo:: Also check that the root address owns the piece.
            Right now we cannot do this because we only receive
            the leaf address when registering an edition.

        """
        chain = BlockchainSpider.chain(self._tree, REGISTERED_PIECE_CODE)

        # edition 0 should only have two transactions: REGISTER and EDITIONS
        if len(chain) == 0:
            self.reason = 'Master edition not yet registered'
            return False

        chain = BlockchainSpider.strip_loan(chain)
        number_editions = chain[0]['number_editions']
        if number_editions == 0:
            self.reason = 'Number of editions not yet registered'
            return False

        if self.edition_number > number_editions:
            self.reason = 'You can only register {} editions. You are trying to register edition {}'.format(number_editions, self.edition_number)
            return False

        if self.edition_number in self._tree:
            self.reason = 'Edition number {} is already registered in the blockchain'. format(self.edition_number)
            return False

        return True

    @property
    def can_register_master(self):
        """
        bool: :const:`True` if :attr:`address` can register the master
        edition of :attr:`piece_address` else :const:`False`.

        To register a master edition the piece address cannot exist in the
        bitcoin network.

        """

        if self._tree != {}:
            self.reason = 'Master piece already registered in the blockchain'
            return False

        return True

    @property
    def can_editions(self):
        """
        bool: :const:`True` if :attr:`address` can register the number of
        editions of :attr:`piece_address` else :const:`False`.

        In order to register the number of editions:

        1. There needs to a least one transaction for the :attr:`piece_address`
        (the registration of the master edition).

        2. A piece with address :attr:`piece_address` needs to be registered
        with ``'ASCRIBESPOOL01PIECE'`` (master edition).

        3. The number of editions should have not been set yet (no tx with
        verb ``'ASCRIBESPOOLEDITIONS'``).

        """
        chain = BlockchainSpider.chain(self._tree, REGISTERED_PIECE_CODE)

        if len(chain) == 0:
            self.reason = 'Master edition not yet registered'
            return False

        number_editions = chain[0]['number_editions']
        if number_editions != 0:
            self.reason = 'Number of editions was already registered for this piece'
            return False

        return True
