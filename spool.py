"""
Main spool verb methods
"""
import requests

from exceptions import Exception

from transactions import Transactions
from settings import *
from utils import dispatch
from spoolverb import Spoolverb


requests.packages.urllib3.disable_warnings()

class SpoolFundsError(Exception):

    """
    To be raised when an address does not have ownership of a hash
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)




class Spool(object):

    """
    Class that contains all Spool methods.

    In the SPOOL implementation there is no notion of users only addresses.
    All addresses come from BIP32 HD wallets. This makes it easier to manage all the keys
    since we can retrieve everything we need from a master secret (namely the private key
    to sign the transactions).

    Since we are dealing with HD wallets we expect all from_address to be a tuple of (path, address)
    so that we can retrieve the private key for that particular leaf address.
    If we want to use the root address we can just pass an empty string to the first element of the
    tuple e.g. ('', address). For instance when using the federation wallet address we have no
    need to create leaf addresses.

    A file is represented by two hashes:
        - file_hash: is the hash of the digital file
        - file_hash_metadata: is the hash of the digital file + metadata
    The hash is passed to the methods has a tuple (file_hash, file_hash_metadata)
    """

    def __init__(self, testnet=False):
        """

        :param testnet:
        :return:
        """
        self.testnet = testnet
        self._netcode = 'XTN' if testnet else 'BTC'
        self._t = Transactions(testnet=testnet)

    @dispatch
    def register(self, from_address, to_address, hash, password, edition_num, min_confirmations=6, sync=False):
        """TODO: Docstring for register.
        To register a master edition use edition_num=0. Master edition is the edition number 0

        :arg1: TODO
        :returns: TODO
        """
        file_hash, file_hash_metadata = hash
        path, from_address = from_address
        verb = Spoolverb(edition_num=edition_num)
        unsigned_tx = self.simple_spool_transaction(from_address,
                                                    [file_hash, file_hash_metadata, to_address],
                                                    op_return=verb.register,
                                                    min_confirmations=min_confirmations)

        signed_tx = self._t.sign_transaction(unsigned_tx, password)
        txid = self._t.push(signed_tx)
        return txid

    @dispatch
    def editions(self, from_address, to_address, hash, password, num_editions, min_confirmations=6, sync=False):
        """TODO: Docstring for register.
        To register a master edition use edition_num=0. Master edition is the edition number 0

        :arg1: TODO
        :returns: TODO
        """
        file_hash, file_hash_metadata = hash
        path, from_address = from_address
        verb = Spoolverb(num_editions=num_editions)
        unsigned_tx = self.simple_spool_transaction(from_address,
                                                    [file_hash, file_hash_metadata, to_address],
                                                    op_return=verb.editions,
                                                    min_confirmations=min_confirmations)

        signed_tx = self._t.sign_transaction(unsigned_tx, password)
        txid = self._t.push(signed_tx)
        return txid

    @dispatch
    def transfer(self, from_address, to_address, hash, password, edition_num, min_confirmations=6, sync=False):
        """TODO: Docstring for transfer.

        :arg1: TODO
        :returns: TODO

        """
        # 0. check ownership
        # an exception will be thrown if from_address does not own the piece with hash
        # 1. refill
        # TODO: Dependent transactions so that we wait for the refill to finish before doing the transfer
        # refill_txid = self.refill(TEST_REFILL_ADDR, from_address, 1, 0, TEST_REFILL_PASS, min_confirmations=1)
        # print 'refill_txid: {}'.format(refill_txid)
        # time.sleep(60 * 5)
        # 2. transfer
        path, from_address = from_address
        file_hash, file_hash_metadata = hash
        verb = Spoolverb(edition_num=edition_num)
        unsigned_tx = self.simple_spool_transaction(from_address,
                                                    [file_hash, to_address],
                                                    op_return=verb.transfer,
                                                    min_confirmations=min_confirmations)
        signed_tx = self._t.sign_transaction(unsigned_tx, password, path=path)
        txid = self._t.push(signed_tx)
        return txid

    @dispatch
    def consign(self, from_address, to_address, hash, password, edition_num, min_confirmations=6, sync=False):

        path, from_address = from_address
        file_hash, file_hash_metadata = hash
        verb = Spoolverb(edition_num=edition_num)
        unsigned_tx = self.simple_spool_transaction(from_address,
                                                    [file_hash, to_address],
                                                    op_return=verb.consign,
                                                    min_confirmations=min_confirmations)
        signed_tx = self._t.sign_transaction(unsigned_tx, password, path=path)
        txid = self._t.push(signed_tx)
        return txid

    @dispatch
    def unconsign(self, from_address, to_address, hash, password, edition_num, min_confirmations=6, sync=False):
        """
        In an unconsignment the to_address needs to be the address that created the consign transaction
        """
        path, from_address = from_address
        file_hash, file_hash_metadata = hash
        verb = Spoolverb(edition_num=edition_num)
        unsigned_tx = self.simple_spool_transaction(from_address,
                                                    [file_hash, to_address],
                                                    op_return=verb.unconsign,
                                                    min_confirmations=min_confirmations)
        signed_tx = self._t.sign_transaction(unsigned_tx, password, path=path)
        txid = self._t.push(signed_tx)
        return txid

    @dispatch
    def loan(self, from_address, to_address, hash, password, edition_num, loan_start, loan_end, min_confirmations=6, sync=False):
        """TODO: Docstring for loan.

        :start_date: start date of the loan with format YYMMDD
        :end_date: end date of the loan with format YYMMDD

        :returns: TODO
        """
        # 0. check ownership
        # an exception will be thrown if from_address does not own the piece with hash
        path, from_address = from_address
        file_hash, file_hash_metadata = hash
        verb = Spoolverb(edition_num=edition_num, loan_start=loan_start, loan_end=loan_end)
        unsigned_tx = self.simple_spool_transaction(from_address,
                                                    [file_hash, to_address],
                                                    op_return=verb.loan,
                                                    min_confirmations=min_confirmations)
        signed_tx = self._t.sign_transaction(unsigned_tx, password, path=path)
        txid = self._t.push(signed_tx)
        return txid

    @dispatch
    def refill_main_wallet(self, from_address, to_address, nfees, ntokens, password, min_confirmations=6, sync=False):
        """Used to refill main wallet. Here we don't want to use refill because we do not want a spoolverb and we
        want to set the change.

        :arg1: TODO
        :returns: TODO

        """
        path, from_address = from_address
        unsigned_tx = self._t.simple_transaction(from_address,
                                                       [(to_address, 10000)] * nfees + [(to_address, 600)] * ntokens,
                                                       min_confirmations=min_confirmations)

        signed_tx = self._t.sign_transaction(unsigned_tx, password)
        txid = self._t.push(signed_tx)
        return txid

    @dispatch
    def refill(self, from_address, to_address, nfees, ntokens, password, min_confirmations=6, sync=False):
        """
        with refill we do not send the change since we expect the main wallet to be sanitized, containing only
        tokens and fees
        """
        path, from_address = from_address
        verb = Spoolverb()
        # nfees + 1: nfees to refill plus one fee for the refill transaction itself
        inputs = self._select_inputs(from_address, nfees + 1, ntokens, min_confirmations=min_confirmations)
        outputs = [{'address': to_address, 'value': self._t._dust}] * ntokens
        outputs += [{'address': to_address, 'value': self._t._min_tx_fee}] * nfees
        outputs += [{'script': self._t._op_return_hex(verb.fuel), 'value': 0}]
        print inputs,
        print outputs
        unsigned_tx = self._t.build_transaction(inputs, outputs)
        signed_tx = self._t.sign_transaction(unsigned_tx, password, path=path)
        txid = self._t.push(signed_tx)
        return txid

    def delete(self, arg1):
        """TODO: Docstring for delete.

        :arg1: TODO
        :returns: TODO

        """
        raise NotImplementedError

    def custom(self, arg1):
        """Method for custom verbs

        :arg1: TODO
        :returns: TODO

        """
        raise NotImplementedError

    def simple_spool_transaction(self, from_address, to, op_return, min_confirmations=6):
        # list of addresses to send
        ntokens = len(to)
        nfees = self._t.estimate_fee(ntokens, 2) / 10000
        print 'nfees: {}'.format(nfees)
        inputs = self._select_inputs(from_address, nfees, ntokens, min_confirmations=min_confirmations)
        # outputs
        outputs = [{'address': to_address, 'value': self._t._dust} for to_address in to]
        outputs += [{'script': self._t._op_return_hex(op_return), 'value': 0}]
        print inputs
        print outputs
        # build transaction
        unsigned_tx = self._t.build_transaction(inputs, outputs)
        return unsigned_tx

    def _select_inputs(self, address, nfees, ntokens, min_confirmations=6):
        # selects the inputs for the spool transaction
        unspents = self._t.get(address, min_confirmations=min_confirmations)['unspents']
        if len(unspents) == 0:
            raise Exception("No spendable outputs found")

        fees = filter(lambda d: d['amount'] == self._t._min_tx_fee, unspents)[:nfees]
        tokens = filter(lambda d: d['amount'] == self._t._dust, unspents)[:ntokens]
        if len(fees) != nfees or len(tokens) != ntokens:
            raise SpoolFundsError("Not enough outputs to spend. Refill your wallet")

        return fees + tokens




