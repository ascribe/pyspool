# -*- coding: utf-8 -*-
"""
Main spool verb methods
"""
from __future__ import absolute_import, division,  unicode_literals
from future import standard_library
standard_library.install_aliases()

from builtins import object, range
from past.utils import old_div
from queue import Queue

from transactions import Transactions

from .spoolverb import Spoolverb
from .utils import dispatch


class SpoolFundsError(Exception):
    """
    To be raised when an address does not have ownership of a hash.
    """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class Spool(object):
    """
    Class that contains all Spool methods.

    In the SPOOL implementation there is no notion of users only addresses.
    All addresses come from BIP32 HD wallets. This makes it easier to manage all the keys
    since we can retrieve everything we need from a master secret (namely the private key
    to sign the transactions).

    Since we are dealing with HD wallets we expect all ``from_address`` to be a
    tuple of ``(path, address)`` so that we can retrieve the private key for
    that particular leaf address. If we want to use the root address we can
    just pass an empty string to the first element of the tuple e.g.
    ``('', address)``. For instance when using the federation wallet address we
    have no need to create leaf addresses.

    A file is represented by two hashes:
        - ``file_hash``: is the hash of the digital file
        - ``file_hash_metadata``: is the hash of the digital file + metadata

    The hash is passed to the methods has a tuple: ``(file_hash, file_hash_metadata)``

    Attributes:
        FEE (int): transaction fee
        TOKEN (int): token
        SPENTS_QUEUE_MAXSIZE (int): spent outputs queue maximum size

    """
    FEE = 30000
    TOKEN = 3000
    SPENTS_QUEUE_MAXSIZE = 50

    def __init__(self, testnet=False, service='blockr', username='', password='', host='', port=''):
        """
        Args:
            testnet (bool): Whether to use the mainnet or testnet. Defaults to
                the mainnet (``False``).
            service (str): Bitcoin communication interface: ``'blockr'``,
                ``'daemon'``, or ``'regtest'``. ``'blockr'`` refers to the
                public api, whereas ``'daemon'`` and ``'regtest'`` refer to the
                jsonrpc inteface. Defaults to ``'blockr'``.
            username (str): username for jsonrpc communications
            password (str): password for jsonrpc communications
            hostname (str): hostname of the bitcoin node when using jsonrpc
            port (str): port number of the bitcoin node when using jsonrpc

        """
        self.testnet = testnet
        self._netcode = 'XTN' if testnet else 'BTC'
        self._t = Transactions(service=service, testnet=testnet, username=username,
                               password=password, host=host, port=port)
        # simple cache for spent outputs. Useful so that rapid firing transactions don't use the same outputs
        self._spents = Queue(maxsize=self.SPENTS_QUEUE_MAXSIZE)

    @dispatch
    def register_piece(self, from_address, to_address, hash, password, min_confirmations=6, sync=False, ownership=True):
        """
        Register a piece

        Args:
            from_address (Tuple[str]): Federation address. All register transactions
                originate from the the Federation wallet
            to_address (str): Address registering the edition
            hash (Tuple[str]): Hash of the piece. (file_hash, file_hash_metadata)
            password (str): Federation wallet password. For signing the transaction
            edition_num (int): The number of the edition to register. User
                edition_num=0 to register the master edition
            min_confirmations (int): Override the number of confirmations when
                chosing the inputs of the transaction. Defaults to 6
            sync (bool): Perform the transaction in synchronous mode, the call to the
                function will block until there is at least on confirmation on
                the blockchain. Defaults to False
            ownership (bool): Check ownsership in the blockchain before pushing the
                transaction. Defaults to True

        Returns:
            str: transaction id

        """
        file_hash, file_hash_metadata = hash
        path, from_address = from_address
        verb = Spoolverb()
        unsigned_tx = self.simple_spool_transaction(from_address,
                                                    [file_hash, file_hash_metadata, to_address],
                                                    op_return=verb.piece,
                                                    min_confirmations=min_confirmations)

        signed_tx = self._t.sign_transaction(unsigned_tx, password)
        txid = self._t.push(signed_tx)
        return txid

    @dispatch
    def register(self, from_address, to_address, hash, password, edition_num, min_confirmations=6, sync=False, ownership=True):
        """
        Register an edition or master edition of a piece

        Args:
            from_address (Tuple[str]): Federation address. All register transactions originate from the the Federation wallet
            to_address (str): Address registering the edition
            hash (Tuple[str])): Hash of the piece. Tuple (file_hash, file_hash_metadata)
            password (str): Federation wallet password. For signing the transaction
            edition_num (int): The number of the edition to register. User edition_num=0 to register the master edition
            min_confirmations (int): Override the number of confirmations when chosing the inputs of the transaction. Defaults to 6
            sync (bool): Perform the transaction in synchronous mode, the call to the function will block until there is at
                least on confirmation on the blockchain. Defaults to False
            ownership (bool): Check ownsership in the blockchain before pushing the transaction. Defaults to True

        Returns:
            str: transaction id

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
    def consigned_registration(self, from_address, to_address, hash, password, min_confirmations=6, sync=False, ownership=True):
        """
        Register an edition or master edition of a piece consigned to ``from_address``

        Args:
            from_address (Tuple[str])): Federation address. All register transactions originate from the the Federation wallet
            to_address (str): Address registering the edition
            hash (Tuple[str]): Hash of the piece. Tuple (file_hash, file_hash_metadata)
            password (str): Federation wallet password. For signing the transaction
            min_confirmations (int): Override the number of confirmations when chosing the inputs of the transaction. Defaults to 6
            sync (bool): Perform the transaction in synchronous mode, the call to the function will block until there is at
                least on confirmation on the blockchain. Defaults to False
            ownership (bool): Check ownsership in the blockchain before pushing the transaction. Defaults to True

        Returns:
            str: transaction id

        """
        file_hash, file_hash_metadata = hash
        path, from_address = from_address
        verb = Spoolverb()
        unsigned_tx = self.simple_spool_transaction(from_address,
                                                    [file_hash, file_hash_metadata, to_address],
                                                    op_return=verb.consigned_registration,
                                                    min_confirmations=min_confirmations)

        signed_tx = self._t.sign_transaction(unsigned_tx, password)
        txid = self._t.push(signed_tx)
        return txid

    @dispatch
    def editions(self, from_address, to_address, hash, password, num_editions, min_confirmations=6, sync=False, ownership=True):
        """
        Register the number of editions of a piece

        Args:
            from_address (Tuple[str]): Federation address. All register transactions originate from the the Federation wallet
            to_address (str): Address registering the number of editions
            hash (Tuple[str]): Hash of the piece. Tuple (file_hash, file_hash_metadata)
            password (str):  Federation wallet password. For signing the transaction
            num_editions (int): Number of editions of the piece
            min_confirmations (int): Number of confirmations when chosing the inputs of the transaction. Defaults to 6
            sync (bool): Perform the transaction in synchronous mode, the call to the function will block until there is at
                least on confirmation on the blockchain. Defaults to False
            ownership (bool): Check ownsership in the blockchain before pushing the transaction. Defaults to True

        Returns:
            str: transaction id

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
    def transfer(self, from_address, to_address, hash, password, edition_num, min_confirmations=6, sync=False, ownership=True):
        """
        Transfer a piece between addresses

        Args:
            from_address (Tuple[str]): Address currently owning the edition
            to_address: Address to receive the edition
            hash (Tuple[str]): Hash of the piece. Tuple (file_hash, file_hash_metadata)
            password (str): Password for the wallet currently owning the edition. For signing the transaction
            edition_num (int): the number of the edition to transfer
            min_confirmations (int): Number of confirmations when chosing the inputs of the transaction. Defaults to 6
            sync (bool): Perform the transaction in synchronous mode, the call to the function will block until there is at
                least on confirmation on the blockchain. Defaults to False
            ownership (bool): Check ownsership in the blockchain before pushing the transaction. Defaults to True

        Returns:
            str: transaction id

        """
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
    def consign(self, from_address, to_address, hash, password, edition_num, min_confirmations=6, sync=False, ownership=True):
        """
        Consign a piece to an address

        Args:
            from_address (Tuple[str]): Address currently owning the edition
            to_address (str): Address to where the piece will be consigned to
            hash (Tuple[str]): Hash of the piece. Tuple (file_hash, file_hash_metadata)
            password (str): Password for the wallet currently owning the edition. For signing the transaction
            edition_num (int): the number of the edition to consign
            min_confirmations (int): Number of confirmations when chosing the inputs of the transaction. Defaults to 6
            sync (bool): Perform the transaction in synchronous mode, the call to the function will block until there is at
                least on confirmation on the blockchain. Defaults to False
            ownership (bool): Check ownsership in the blockchain before pushing the transaction. Defaults to True

        Returns:
            str: transaction id

        """
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
    def unconsign(self, from_address, to_address, hash, password, edition_num, min_confirmations=6, sync=False, ownership=True):
        """
        Unconsign the edition

        Args:
            from_address (Tuple[str]): Address where the edition is currently consigned
            to_address (str): Address that consigned the piece to from_address
            hash (Tuple[str]): Hash of the piece. Tuple (file_hash, file_hash_metadata)
            password (str): Password for the wallet currently holding the edition. For signing the transaction
            edition_num (int): the number of the edition to unconsign
            min_confirmations (int): Number of confirmations when chosing the inputs of the transaction. Defaults to 6
            sync (bool): Perform the transaction in synchronous mode, the call to the function will block until there is at
                least on confirmation on the blockchain. Defaults to False
            ownership (bool): Check ownsership in the blockchain before pushing the transaction. Defaults to True

        Returns:
            str: transaction id

        """
        # In an unconsignment the to_address needs to be the address that created the consign transaction
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
    def loan(self, from_address, to_address, hash, password, edition_num, loan_start, loan_end, min_confirmations=6, sync=False, ownership=True):
        """
        Loan the edition

        Args:
            from_address (Tuple[str]): Address currently holding the edition
            to_address (str): Address to loan the edition to
            hash (Tuple[str]): Hash of the piece. Tuple (file_hash, file_hash_metadata)
            password (str): Password for the wallet currently holding the edition. For signing the transaction
            edition_num (int): the number of the edition to loan
            loan_start (str): Start date for the loan. In the form YYMMDD
            loan_end (str): End date for the loan. In the form YYMMDD
            min_confirmations (int): Number of confirmations when chosing the inputs of the transaction. Defaults to 6
            sync (bool): Perform the transaction in synchronous mode, the call to the function will block until there is at
                least on confirmation on the blockchain. Defaults to False
            ownership (bool): Check ownsership in the blockchain before pushing the transaction. Defaults to True

        Returns:
            str: transaction id

        """
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
    def migrate(self, from_address, prev_address, new_address, hash, password, edition_num, min_confirmations=6, sync=False, ownership=True):
        """
        Migrate an edition

        Args:
            from_address (Tuple[str]): Federation address. All register transactions originate from the the Federation wallet
            to_address (str): Address registering the edition
            hash (Tuple[str]): Hash of the piece. Tuple (file_hash, file_hash_metadata)
            password (str): Federation wallet password. For signing the transaction
            edition_num (int): The number of the edition to register. User edition_num=0 to register the master edition
            min_confirmations (int): Override the number of confirmations when chosing the inputs of the transaction. Defaults to 6
            sync (bool): Perform the transaction in synchronous mode, the call to the function will block until there is at
                least on confirmation on the blockchain. Defaults to False
            ownership (bool): Check ownsership in the blockchain before pushing the transaction. Defaults to True

        Returns:
            str: transaction id

        """
        file_hash, file_hash_metadata = hash
        path, from_address = from_address
        verb = Spoolverb(edition_num=edition_num)
        unsigned_tx = self.simple_spool_transaction(from_address,
                                                    [file_hash, prev_address, new_address],
                                                    op_return=verb.migrate,
                                                    min_confirmations=min_confirmations)

        signed_tx = self._t.sign_transaction(unsigned_tx, password)
        txid = self._t.push(signed_tx)
        return txid

    @dispatch
    def refill_main_wallet(self, from_address, to_address, nfees, ntokens, password, min_confirmations=6, sync=False):
        """
        Refill the Federation wallet with tokens and fees. This keeps the federation wallet clean.
        Dealing with exact values simplifies the transactions. No need to calculate change. Easier to keep track of the
        unspents and prevent double spends that would result in transactions being rejected by the bitcoin network.

        Args:

            from_address (Tuple[str]): Refill wallet address. Refills the federation wallet with tokens and fees
            to_address (str): Federation wallet address
            nfees (int): Number of fees to transfer. Each fee is 10000 satoshi. Used to pay for the transactions
            ntokens (int): Number of tokens to transfer. Each token is 600 satoshi. Used to register hashes in the blockchain
            password (str): Password for the Refill wallet. Used to sign the transaction
            min_confirmations (int): Number of confirmations when chosing the inputs of the transaction. Defaults to 6
            sync (bool): Perform the transaction in synchronous mode, the call to the function will block until there is at
                least on confirmation on the blockchain. Defaults to False

        Returns:
            str: transaction id
        """
        path, from_address = from_address
        unsigned_tx = self._t.simple_transaction(from_address,
                                                 [(to_address, self.FEE)] * nfees + [(to_address, self.TOKEN)] * ntokens,
                                                 min_confirmations=min_confirmations)

        signed_tx = self._t.sign_transaction(unsigned_tx, password)
        txid = self._t.push(signed_tx)
        return txid

    @dispatch
    def refill(self, from_address, to_address, nfees, ntokens, password, min_confirmations=6, sync=False):
        """
        Refill wallets with the necessary fuel to perform spool transactions

        Args:
            from_address (Tuple[str]): Federation wallet address. Fuels the wallets with tokens and fees. All transactions to wallets
                holding a particular piece should come from the Federation wallet
            to_address (str): Wallet address that needs to perform a spool transaction
            nfees (int): Number of fees to transfer. Each fee is 10000 satoshi. Used to pay for the transactions
            ntokens (int): Number of tokens to transfer. Each token is 600 satoshi. Used to register hashes in the blockchain
            password (str): Password for the Federation wallet. Used to sign the transaction
            min_confirmations (int): Number of confirmations when chosing the inputs of the transaction. Defaults to 6
            sync (bool): Perform the transaction in synchronous mode, the call to the function will block until there is at
                least on confirmation on the blockchain. Defaults to False

        Returns:
            str: transaction id

        """
        path, from_address = from_address
        verb = Spoolverb()
        # nfees + 1: nfees to refill plus one fee for the refill transaction itself
        inputs = self.select_inputs(from_address, nfees + 1, ntokens, min_confirmations=min_confirmations)
        outputs = [{'address': to_address, 'value': self.TOKEN}] * ntokens
        outputs += [{'address': to_address, 'value': self.FEE}] * nfees
        outputs += [{'script': self._t._op_return_hex(verb.fuel), 'value': 0}]
        unsigned_tx = self._t.build_transaction(inputs, outputs)
        signed_tx = self._t.sign_transaction(unsigned_tx, password, path=path)
        txid = self._t.push(signed_tx)
        return txid

    def simple_spool_transaction(self, from_address, to, op_return, min_confirmations=6):
        """
        Utililty function to create the spool transactions. Selects the inputs,
        encodes the op_return and constructs the transaction.

        Args:
            from_address (str): Address originating the transaction
            to (str): list of addresses to receive tokens (file_hash, file_hash_metadata, ...)
            op_return (str): String representation of the spoolverb, as returned by the properties of Spoolverb
            min_confirmations (int): Number of confirmations when chosing the inputs of the transaction. Defaults to 6

        Returns:
            str: unsigned transaction

        """
        # list of addresses to send
        ntokens = len(to)
        nfees = old_div(self._t.estimate_fee(ntokens, 2), self.FEE)
        inputs = self.select_inputs(from_address, nfees, ntokens, min_confirmations=min_confirmations)
        # outputs
        outputs = [{'address': to_address, 'value': self.TOKEN} for to_address in to]
        outputs += [{'script': self._t._op_return_hex(op_return), 'value': 0}]
        # build transaction
        unsigned_tx = self._t.build_transaction(inputs, outputs)
        return unsigned_tx

    def select_inputs(self, address, nfees, ntokens, min_confirmations=6):
        # selects the inputs for the spool transaction
        unspents = self._t.get(address, min_confirmations=min_confirmations)['unspents']
        unspents = [u for u in unspents if u not in self._spents.queue]
        if len(unspents) == 0:
            raise Exception("No spendable outputs found")

        fees = [u for u in unspents if u['amount'] == self.FEE][:nfees]
        tokens = [u for u in unspents if u['amount'] == self.TOKEN][:ntokens]
        if len(fees) != nfees or len(tokens) != ntokens:
            raise SpoolFundsError("Not enough outputs to spend. Refill your wallet")
        if self._spents.qsize() > self.SPENTS_QUEUE_MAXSIZE - (nfees + ntokens):
            [self._spents.get() for i in range(self._spents.qsize() + nfees + ntokens - self.SPENTS_QUEUE_MAXSIZE)]
        [self._spents.put(fee) for fee in fees]
        [self._spents.put(token) for token in tokens]
        return fees + tokens
