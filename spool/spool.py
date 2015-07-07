"""
Main spool verb methods
"""
from exceptions import Exception
from Queue import Queue

from transactions import Transactions
from utils import dispatch
from spoolverb import Spoolverb


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

    def __init__(self, testnet=False, service='blockr', username='', password='', host='', port=''):
        """

        :param testnet:
        :return:
        """
        self.testnet = testnet
        self._netcode = 'XTN' if testnet else 'BTC'
        self._t = Transactions(service=service, testnet=testnet, username=username,
                               password=password, host=host, port=port)
        # simple cache for spent outputs. Useful so that rapid firing transactions don't use the same outputs
        self._spents = Queue(maxsize=50)

    @dispatch
    def register_piece(self, from_address, to_address, hash, password, min_confirmations=6, sync=False, ownership=True):
        """
        Register a piece

        :param from_address: Federation address. All register transactions originate from the the Federation wallet
        :param to_address: Address registering the edition
        :param hash: Hash of the piece. Tuple (file_hash, file_hash_metadata)
        :param password: Federation wallet password. For signing the transaction
        :param edition_num: The number of the edition to register. User edition_num=0 to register the master edition
        :param min_confirmations: Override the number of confirmations when chosing the inputs of the transaction. Defaults to 6
        :param sync: Perform the transaction in synchronous mode, the call to the function will block until there is at
        least on confirmation on the blockchain. Defaults to False
        :param ownership: Check ownsership in the blockchain before pushing the transaction. Defaults to True
        :return: transaction id
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

        :param from_address: Federation address. All register transactions originate from the the Federation wallet
        :param to_address: Address registering the edition
        :param hash: Hash of the piece. Tuple (file_hash, file_hash_metadata)
        :param password: Federation wallet password. For signing the transaction
        :param edition_num: The number of the edition to register. User edition_num=0 to register the master edition
        :param min_confirmations: Override the number of confirmations when chosing the inputs of the transaction. Defaults to 6
        :param sync: Perform the transaction in synchronous mode, the call to the function will block until there is at
        least on confirmation on the blockchain. Defaults to False
        :param ownership: Check ownsership in the blockchain before pushing the transaction. Defaults to True
        :return: transaction id
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
    def consigned_registration(self, from_address, to_address, hash, password, edition_num, min_confirmations=6, sync=False, ownership=True):
        """
        Register an edition or master edition of a piece consigned to from_address

        :param from_address: Federation address. All register transactions originate from the the Federation wallet
        :param to_address: Address registering the edition
        :param hash: Hash of the piece. Tuple (file_hash, file_hash_metadata)
        :param password: Federation wallet password. For signing the transaction
        :param edition_num: The number of the edition to register. User edition_num=0 to register the master edition
        :param min_confirmations: Override the number of confirmations when chosing the inputs of the transaction. Defaults to 6
        :param sync: Perform the transaction in synchronous mode, the call to the function will block until there is at
        least on confirmation on the blockchain. Defaults to False
        :param ownership: Check ownsership in the blockchain before pushing the transaction. Defaults to True
        :return: transaction id
        """
        file_hash, file_hash_metadata = hash
        path, from_address = from_address
        verb = Spoolverb(edition_num=edition_num)
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

        :param from_address: Federation address. All register transactions originate from the the Federation wallet
        :param to_address: Address registering the number of editions
        :param hash: Hash of the piece. Tuple (file_hash, file_hash_metadata)
        :param password:  Federation wallet password. For signing the transaction
        :param num_editions: Number of editions of the piece
        :param min_confirmations: Number of confirmations when chosing the inputs of the transaction. Defaults to 6
        :param sync: Perform the transaction in synchronous mode, the call to the function will block until there is at
        least on confirmation on the blockchain. Defaults to False
        :param ownership: Check ownsership in the blockchain before pushing the transaction. Defaults to True
        :return: transaction id
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

        :param from_address: Address currently owning the edition
        :param to_address: Address to receive the edition
        :param hash: Hash of the piece. Tuple (file_hash, file_hash_metadata)
        :param password: Password for the wallet currently owning the edition. For signing the transaction
        :param edition_num: the number of the edition to transfer
        :param min_confirmations: Number of confirmations when chosing the inputs of the transaction. Defaults to 6
        :param sync: Perform the transaction in synchronous mode, the call to the function will block until there is at
        least on confirmation on the blockchain. Defaults to False
        :param ownership: Check ownsership in the blockchain before pushing the transaction. Defaults to True
        :return: transaction id
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

        :param from_address: Address currently owning the edition
        :param to_address: Address to where the piece will be consigned to
        :param hash: Hash of the piece. Tuple (file_hash, file_hash_metadata)
        :param password: Password for the wallet currently owning the edition. For signing the transaction
        :param edition_num: the number of the edition to consign
        :param min_confirmations: Number of confirmations when chosing the inputs of the transaction. Defaults to 6
        :param sync: Perform the transaction in synchronous mode, the call to the function will block until there is at
        least on confirmation on the blockchain. Defaults to False
        :param ownership: Check ownsership in the blockchain before pushing the transaction. Defaults to True
        :return: transaction id
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

        :param from_address: Address where the edition is currently consigned
        :param to_address: Address that consigned the piece to from_address
        :param hash: Hash of the piece. Tuple (file_hash, file_hash_metadata)
        :param password: Password for the wallet currently holding the edition. For signing the transaction
        :param edition_num: the number of the edition to unconsign
        :param min_confirmations: Number of confirmations when chosing the inputs of the transaction. Defaults to 6
        :param sync: Perform the transaction in synchronous mode, the call to the function will block until there is at
        least on confirmation on the blockchain. Defaults to False
        :param ownership: Check ownsership in the blockchain before pushing the transaction. Defaults to True
        :return: transaction id
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

        :param from_address: Address currently holding the edition
        :param to_address: Address to loan the edition to
        :param hash: Hash of the piece. Tuple (file_hash, file_hash_metadata)
        :param password: Password for the wallet currently holding the edition. For signing the transaction
        :param edition_num: the number of the edition to unconsign
        :param loan_start: Start date for the loan. In the form YYMMDD
        :param loan_end: End date for the loan. In the form YYMMDD
        :param min_confirmations: Number of confirmations when chosing the inputs of the transaction. Defaults to 6
        :param sync: Perform the transaction in synchronous mode, the call to the function will block until there is at
        least on confirmation on the blockchain. Defaults to False
        :param ownership: Check ownsership in the blockchain before pushing the transaction. Defaults to True
        :return: transaction id
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

        :param from_address: Federation address. All register transactions originate from the the Federation wallet
        :param to_address: Address registering the edition
        :param hash: Hash of the piece. Tuple (file_hash, file_hash_metadata)
        :param password: Federation wallet password. For signing the transaction
        :param edition_num: The number of the edition to register. User edition_num=0 to register the master edition
        :param min_confirmations: Override the number of confirmations when chosing the inputs of the transaction. Defaults to 6
        :param sync: Perform the transaction in synchronous mode, the call to the function will block until there is at
        least on confirmation on the blockchain. Defaults to False
        :param ownership: Check ownsership in the blockchain before pushing the transaction. Defaults to True
        :return: transaction id
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

        :param from_address: Refill wallet address. Refills the federation wallet with tokens and fees
        :param to_address: Federation wallet address
        :param nfees: Number of fees to transfer. Each fee is 10000 satoshi. Used to pay for the transactions
        :param ntokens: Number of tokens to transfer. Each token is 600 satoshi. Used to register hashes in the blockchain
        :param password: Password for the Refill wallet. Used to sign the transaction
        :param min_confirmations: Number of confirmations when chosing the inputs of the transaction. Defaults to 6
        :param sync: Perform the transaction in synchronous mode, the call to the function will block until there is at
        least on confirmation on the blockchain. Defaults to False
        :return: transaction id
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
        Refill wallets with the necessary fuel to perform spool transactions

        :param from_address: Federation wallet address. Fuels the wallets with tokens and fees. All transactions to wallets
                holding a particular piece should come from the Federation wallet
        :param to_address: Wallet address that needs to perform a spool transaction
        :param nfees: Number of fees to transfer. Each fee is 10000 satoshi. Used to pay for the transactions
        :param ntokens: Number of tokens to transfer. Each token is 600 satoshi. Used to register hashes in the blockchain
        :param password: Password for the Federation wallet. Used to sign the transaction
        :param min_confirmations: Number of confirmations when chosing the inputs of the transaction. Defaults to 6
        :param sync: Perform the transaction in synchronous mode, the call to the function will block until there is at
        least on confirmation on the blockchain. Defaults to False
        :return: transaction id
        """
        path, from_address = from_address
        verb = Spoolverb()
        # nfees + 1: nfees to refill plus one fee for the refill transaction itself
        inputs = self.select_inputs(from_address, nfees + 1, ntokens, min_confirmations=min_confirmations)
        outputs = [{'address': to_address, 'value': self._t._dust}] * ntokens
        outputs += [{'address': to_address, 'value': self._t._min_tx_fee}] * nfees
        outputs += [{'script': self._t._op_return_hex(verb.fuel), 'value': 0}]
        unsigned_tx = self._t.build_transaction(inputs, outputs)
        signed_tx = self._t.sign_transaction(unsigned_tx, password, path=path)
        txid = self._t.push(signed_tx)
        return txid

    def simple_spool_transaction(self, from_address, to, op_return, min_confirmations=6):
        """
        Utililty function to create the spool transactions. Selects the inputs, encodes the op_return and
        constructs the transaction.

        :param from_address: Address originating the the transaction
        :param to: list of addresses to receive tokens (file_hash, file_hash_metadata, ...)
        :param op_return: String representation of the spoolverb, as returned by the properties of Spoolverb
        :param min_confirmations: Number of confirmations when chosing the inputs of the transaction. Defaults to 6
        :return: unsigned transaction
        """
        # list of addresses to send
        ntokens = len(to)
        nfees = self._t.estimate_fee(ntokens, 2) / 10000
        inputs = self.select_inputs(from_address, nfees, ntokens, min_confirmations=min_confirmations)
        # outputs
        outputs = [{'address': to_address, 'value': self._t._dust} for to_address in to]
        outputs += [{'script': self._t._op_return_hex(op_return), 'value': 0}]
        # build transaction
        unsigned_tx = self._t.build_transaction(inputs, outputs)
        return unsigned_tx

    def select_inputs(self, address, nfees, ntokens, min_confirmations=6):
        # selects the inputs for the spool transaction
        unspents = self._t.get(address, min_confirmations=min_confirmations)['unspents']
        unspents = filter(lambda d: d not in self._spents.queue, unspents)
        if len(unspents) == 0:
            raise Exception("No spendable outputs found")

        fees = filter(lambda d: d['amount'] == self._t._min_tx_fee, unspents)[:nfees]
        tokens = filter(lambda d: d['amount'] == self._t._dust, unspents)[:ntokens]
        if len(fees) != nfees or len(tokens) != ntokens:
            raise SpoolFundsError("Not enough outputs to spend. Refill your wallet")
        if self._spents.qsize() > 50 - (nfees + ntokens):
            [self._spents.get() for i in range(self._spents.qsize() + nfees + ntokens - 50)]
        [self._spents.put(fee) for fee in fees]
        [self._spents.put(token) for token in tokens]
        return fees + tokens




