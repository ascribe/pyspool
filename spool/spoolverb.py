# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from builtins import object

import re


class SpoolverbError(Exception):
    """
    To be raised when an address does not have ownership of a hash.

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


class Spoolverb(object):
    """
    Allows for easy creation of the verb to be encoded on the
    ``op_return`` of all SPOOL transactions.

    Attributes:
        supported_actions (List[str]): Actions supported by the SPOOL
            protocol.

    """
    supported_actions = ['REGISTER', 'CONSIGN', 'TRANSFER', 'LOAN', 'UNCONSIGN',
                         'FUEL', 'EDITIONS', 'PIECE', 'MIGRATE', 'CONSIGNEDREGISTRATION']

    def __init__(self, num_editions=None, edition_num=None, loan_start='',
                 loan_end='', meta='ASCRIBESPOOL', version='01', action=None):
        """
        Initializer for the Spoolverb class.

        Args:
            num_editions (int): Number of editions to register.
            edition_num (str): Number of the edition to use.
            loan_start (str): Start of the loan in the format ``YYMMDD``.
            loan_end (str): End of the loan in the format ``YYMMDD``.
            meta (str): Header for the spool protocol. Defaults to
                ``'ASCRIBESPOOL'``.
            version (str): Version of the protocol. Defaults to ``'01'``.
            action (str): One of the actions in :attr:`supported_actions`.

        Returns:
            :class:`Spoolverb` instance.

        """
        self.meta = meta
        self.version = version
        self.num_editions = num_editions
        self.edition_number = edition_num if edition_num else ''
        self.loan_start = loan_start
        self.loan_end = loan_end
        self.action = action

    @classmethod
    def from_verb(cls, verb):
        """
        Constructs a :class:`Spoolverb` instance from the string
        representation of the given verb.

        Args:
            verb (str): representation of the verb e.g.:
                ``'ASCRIBESPOOL01LOAN12/150526150528'``. Can also be in
                binary format (:obj:`bytes`): ``b'ASCRIBESPOOL01PIECE'``.

        Returns:
            :class:`Spoolverb` instance.

        """
        pattern = r'^(?P<meta>[A-Z]+)(?P<version>\d+)(?P<action>[A-Z]+)(?P<arg1>\d+)?(\/(?P<arg2>\d+))?$'
        try:
            verb = verb.decode()
        except AttributeError:
            pass
        match = re.match(pattern, verb)
        if not match:
            raise SpoolverbError('Invalid spoolverb: {}'.format(verb))

        data = match.groupdict()
        meta = data['meta']
        version = data['version']
        action = data['action']
        if action == 'EDITIONS':
            num_editions = data['arg1']
            return cls(meta=meta, version=version, action=action, num_editions=int(num_editions))
        elif action == 'LOAN':
            # TODO Review. Workaround for piece loans
            try:
                edition_num = int(data['arg1'])
            except TypeError:
                edition_num = 0
            loan_start = data['arg2'][:6]
            loan_end = data['arg2'][6:]
            return cls(meta=meta, version=version, action=action, edition_num=int(edition_num),
                       loan_start=loan_start, loan_end=loan_end)
        elif action in ['FUEL', 'PIECE', 'CONSIGNEDREGISTRATION']:
            # no edition number for these verbs
            return cls(meta=meta, version=version, action=action)
        else:
            edition_num = data['arg1']
            return cls(meta=meta, version=version, action=action, edition_num=int(edition_num))

    @property
    def piece(self):
        """
        str: representation of the ``PIECE`` spoolverb. E.g.:
            ``'ASCRIBESPOOL01PIECE'``.
        """
        return '{}{}PIECE'.format(self.meta, self.version)

    @property
    def register(self):
        """
        str: representation of the ``REGISTER`` spoolverb. E.g.:
            ``'ASCRIBESPOOL01REGISTER1'```.
        """
        return '{}{}REGISTER{}'.format(self.meta, self.version, self.edition_number)

    @property
    def editions(self):
        """
        str: representation of the ``EDITIONS`` spoolverb. E.g.:
            ``'ASCRIBESPOOL01EDITIONS10'``.
        """
        return '{}{}EDITIONS{}'.format(self.meta, self.version, self.num_editions)

    @property
    def transfer(self):
        """
        str: representation of the ``TRANSFER`` spoolverb. E.g.:
            ``'ASCRIBESPOOL01TRANSFER1'``.
        """
        return '{}{}TRANSFER{}'.format(self.meta, self.version, self.edition_number)

    @property
    def consign(self):
        """
        str: representation of the ``CONSIGN`` spoolverb. E.g.:
            ``'ASCRIBESPOOL01CONSIGN1'``.
        """
        return '{}{}CONSIGN{}'.format(self.meta, self.version, self.edition_number)

    @property
    def unconsign(self):
        """
        str: representation of the ``UNCONSIGN`` spoolverb. E.g.:
            ``'ASCRIBESPOOL01UNCONSIGN1'``.
        """
        return '{}{}UNCONSIGN{}'.format(self.meta, self.version, self.edition_number)

    @property
    def loan(self):
        """
        str: representation of the ``LOAN`` spoolverb. E.g.:
            ``'ASCRIBESPOOL01LOAN1/150526150528'``.
        """
        return '{}{}LOAN{}/{}{}'.format(self.meta, self.version, self.edition_number,
                                        self.loan_start, self.loan_end)

    @property
    def migrate(self):
        """
        str: representation of the ``MIGRATE`` spoolverb. E.g.:
            ``'ASCRIBESPOOL01MIGRATE1'``.
        """
        return '{}{}MIGRATE{}'.format(self.meta, self.version, self.edition_number)

    @property
    def consigned_registration(self):
        """
        str: representation of the ``CONSIGNEDREGISTRATION`` spoolverb. E.g.:
            ``'ASCRIBESPOOL01CONSIGNEDREGISTRATION'``.
        """
        return '{}{}CONSIGNEDREGISTRATION'.format(self.meta, self.version)

    @property
    def fuel(self):
        """
        str: representation of the ``FUEL`` spoolverb. E.g.:
            ``'ASCRIBESPOOL01FUEL'``.
        """
        return '{}{}FUEL'.format(self.meta, self.version)
