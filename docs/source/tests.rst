Testing
=======
At the moment most tests rely on a bitcoin regtest node running. Depending
on how the bitcoin node is run some environment variables may need to be set.

The simplest is to use the provided `docker-compose.yml`_ under the
``pyspool`` github repository.

First run the bitcoin regtest daemon in background mode:

.. code-block:: bash

    $ docker-compose up -d bitcoin

Then run the tests:

.. code-block:: bash

    $ docker-compose run --rm spool py.test -v

To run the tests against `python 2 <https://pythonclock.org/>`_:

.. code-block:: bash

    $ docker-compose run --rm spool-py2 py.test -v

.. note:: You may need to build the image for the services ``spool`` and
    ``spool-py2``. E.g.:

    .. code-block:: bash

        $ docker-compose build spool

Without Docker
--------------
The tests rely on four environment variables specific to bitcoin:

.. envvar:: BITCOIN_HOST
    
    The host of the bitcoin regtest node. Defaults to ``'localhost'``.

.. envvar:: BITCOIN_PORT

    The port of the bitcoin regtest node. Defaults to ``18332``.

.. envvar:: BITCOIN_RPCUSER

    The rpc user used to connect to bitcoin regtest node. Defaults to
    ``'merlin'``.

.. envvar:: BITCOIN_RPCPASSWORD

    The password of the user, used to connect to the bitcoin regtest node.
    Defaults to ``'secret'``.

Assuming the above default environment variables, a bitcoin regtest node can
be run as follows:

.. code-block:: bash
    
    $ bitcoind -daemon -regtest -rpcuser=merlin -rpcpassword=secret -txindex=1

.. important:: Please note the ``-txindex=1`` option. This ensures that all
    transactions are indexed and retrievable by the RPC
    ``getrawtransaction``. Without this option some tests will fail.

Using a :file:`bitcoin.conf`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
A `bitcoin.conf <https://en.bitcoin.it/wiki/Running_Bitcoin#Bitcoin.conf_Configuration_File>`_
file can also be used. E.g.:

.. code-block:: bash

    # $HOME/.bitcoin/bitcoin.conf (under linux)
    rpcuser=merlin
    rpcpassword=secret
    txindex=1

.. tip:: The `.travis.yml`_, `docker-compose.yml`_, and `bitcoin_regtest.conf`_
    files, under the ``pyspool`` github repository may be helpful to look at.



.. _docker-compose.yml: https://github.com/ascribe/pyspool/blob/master/docker-compose.yml
.. _bitcoin_regtest.conf: https://github.com/ascribe/pyspool/blob/master/bitcoin_regtest.conf
.. _.travis.yml: https://github.com/ascribe/pyspool/blob/master/.travis.yml
