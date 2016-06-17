# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from builtins import object

import re


class SpoolverbError(Exception):

    """
    To be raised when an address does not have ownership of a hash
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class Spoolverb(object):

    supported_actions = ['REGISTER', 'CONSIGN', 'TRANSFER', 'LOAN', 'UNCONSIGN',
                         'FUEL', 'EDITIONS', 'PIECE', 'MIGRATE', 'CONSIGNEDREGISTRATION']

    def __init__(self, num_editions=None, edition_num=None, loan_start='',
                 loan_end='', meta='ASCRIBESPOOL', version='01', action=None):
        """
        Initializer for the Spoolverb class

        :param num_editions: number of editions to register
        :param edition_num: number of the edition to use
        :param loan_start: start of the loan in the format YYMMDD
        :param loan_end: end of the loan in the format YYMMDD
        :param meta: Header for the spool protocol. Defaults to 'ASCRIBESPOOL'
        :param version: Version of the protocol. Defaults to '01'
        :param action: one of the actions in supported_actions
        :return: Spoolverb instace
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
        Construct a spoolverb instance from the string representation of the verb

        :param verb: string representation of the verb e.g. ASCRIBESPOOL01LOAN12/150526150528
        :return: Spoolverb instance
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
        return '{}{}PIECE'.format(self.meta, self.version)

    @property
    def register(self):
        return '{}{}REGISTER{}'.format(self.meta, self.version, self.edition_number)

    @property
    def editions(self):
        return '{}{}EDITIONS{}'.format(self.meta, self.version, self.num_editions)

    @property
    def transfer(self):
        return '{}{}TRANSFER{}'.format(self.meta, self.version, self.edition_number)

    @property
    def consign(self):
        return '{}{}CONSIGN{}'.format(self.meta, self.version, self.edition_number)

    @property
    def unconsign(self):
        return '{}{}UNCONSIGN{}'.format(self.meta, self.version, self.edition_number)

    @property
    def loan(self):
        return '{}{}LOAN{}/{}{}'.format(self.meta, self.version, self.edition_number,
                                        self.loan_start, self.loan_end)

    @property
    def migrate(self):
        return '{}{}MIGRATE{}'.format(self.meta, self.version, self.edition_number)

    @property
    def consigned_registration(self):
        return '{}{}CONSIGNEDREGISTRATION'.format(self.meta, self.version)

    @property
    def fuel(self):
        return '{}{}FUEL'.format(self.meta, self.version)
