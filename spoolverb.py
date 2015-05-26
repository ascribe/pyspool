from collections import namedtuple
from exceptions import Exception
import re

"""
SPOOLVERB = namedtuple('SPOOLVERB', ['register', 'consign', 'transfer', 'loan', 'unconsign', 'fuel'])
spoolverb = SPOOLVERB('REGISTER',
                      'CONSIGN',
                      'TRANSFER',
                      'LOAN',
                      'UNCONSIGN',
                      'FUEL')
"""


class SpoolverbError(Exception):

    """
    To be raised when an address does not have ownership of a hash
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class Spoolverb(object):

    supported_actions = ['REGISTER', 'CONSIGN', 'TRANSFER', 'LOAN', 'UNCONSIGN', 'FUEL', 'EDITIONS']

    def __init__(self, num_editions=None, edition_num=None, loan_start='', loan_end='', meta='ASCRIBESPOOL', version='01', action=None):
        # loan_start and loan_end are dates with format YYMMDD
        self.meta = meta
        self.version = version
        self.num_editions = num_editions
        self.edition_number = edition_num
        self.loan_start = loan_start
        self.loan_end = loan_end
        self.action = action

    @classmethod
    def from_verb(cls, verb):
        pattern = r'^(?P<meta>[A-Z]+)(?P<version>\d+)(?P<action>[A-Z]+)(?P<arg1>\d+)(\/(?P<arg2>\d+))?$'
        match = re.match(pattern, verb)
        if not match:
            raise SpoolverbError('Invalid spoolverb: {}'.format(verb))

        data = match.groupdict()
        meta = data['meta']
        version = data['version']
        action = data['action']
        if action == 'EDITIONS':
            num_editions = data['arg1']
            return cls(meta=meta, version=version, action=action, num_editions=num_editions)
        elif action == 'LOAN':
            edition_num = data['arg1']
            loan_start = data['arg2'][:6]
            loan_end = data['arg2'][6:]
            return cls(meta=meta, version=version, action=action, edition_num=edition_num, loan_start=loan_start, loan_end=loan_end)
        else:
            edition_num = data['arg1']
            return cls(meta=meta, version=version, action=action, edition_num=int(edition_num))

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
    def fuel(self):
        return '{}{}FUEL'.format(self.meta, self.version)

    @staticmethod
    def get_action_from_verb(verb):
        match = re.match( r'^[A-Z]+\d+([A-Z]+).*', verb)
        if match:
            return match.groups()[0]
        else:
            raise SpoolverbError('Invalid spoolverb: {}'.format(verb))

