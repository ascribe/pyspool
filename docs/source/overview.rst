Overview
========
All hashes are in base 58 so that they can be inserted in the bitcoin
blockchain.

Refill Wallet
-------------
The refill wallet is only used to refill the Federation Wallet with 10000 and
600 satoshi outputs. This way we maintain the Federation Wallet clean which
makes it easier to manage.

Federation Wallet
-----------------
The Federation wallet is the wallet from where all the registers in the
blockchain occur. We can check the validity of transactions by looking at the
origin of this transactions and see if the originating address belongs to a
federation. For instance all pieces registered through `ascribe.io`_ will
originate from the address ``1JttRRdtAi6cDNM23Uq4BEU61R8kJeANJs`` for the first
version of the protocol or ``1AScRhqdXMrJyxNmjEapMZi1PLFsqmLquG`` for protocol
version ``01``.

The Federation wallet should only contain fuel outputs with the amount of 10000
satoshi and token outputs with the amount of 600 satoshi. The fuel is used to
pay the fee for the transactions and tokens are used to register address on the
blockchain.

Ensuring that the Federation wallet cointains outputs with these amounts makes
the transactions simpler since there is no need for change. It is also easier
to keep track of the unspents in order to prevent invalid transactions due to
double spends (specially important when there is a high throughput of
transactions).


.. _ascribe.io: https://www.ascribe.io/
