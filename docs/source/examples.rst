Examples
========
All the addresses and transaction ids output by this examples can be checked
in the bitcoin blockchain.

For this example we will be implementing the following actions:

1. Refill Federation wallet with fuel and tokens
2. ``user1`` registers master edition
3. ``user1`` registers number of editions
4. ``user1`` registers edition number ``1``
5. ``user1`` transfers edition number ``1`` to ``user2``
6. ``user2`` consigns edition number ``1`` to ``user3``
7. ``user3`` unconsigns edition number ``1`` to ``user2``
8. ``user2`` loans edition number ``1`` to ``user3``

This is the information that we will need:

``refill_pass``
    refill wallet password

``federation_pass``
    federation wallet password

``user1_pass``
    ``user1`` password

``user2_pass``
    ``user2`` password

``user3_pass``
    ``user3`` password

``refill_root``
    .. code-block:: python
    
        ('', u'mhyCaF2HFk7CVwKmyQ8TahgVdjnHSr1pTv')

``federation_root``
    .. code-block:: python
        
        ('', u'mqXz83H4LCxjf2ie8hYNsTRByvtfV43Pa7')

``user1_root``
    root address for ``user1`` HD wallet

    .. code-block:: python
        
        ('', u'n36EiKuYYXNS9h84CnkLK3sEevZsfksaGN') 

``user1_leaf``
    leaf address for ``user1`` HD wallet
    
    .. code-block:: python
    
        ('2015/5/28/9/28/44/982190',
         u'mjq4rZZEyJGFfzg59RLFmuNJTo3jakEDrS')

``user2_leaf``
    leaf address for ``user2`` HD wallet

    .. code-block:: python
    
        ('2015/5/28/9/28/45/184623',
         u'mhRJqLG3BwXXG7YADQD3Ng3c6coZVwoFo6') 
    
``user3_leaf``
    leaf address for ``user3`` HD wallet

    .. code-block:: python
    
        ('2015/5/28/9/28/45/387493',
         u'mhMXXntQCorduhcygY7gLdmuunVEM59C8q') 

``file_hash``
    file_hash, file_hash + metadata

    .. code-block:: python
    
        (u'mhXeWEMLnEwVNnyqKrqUDPAYSuwhfyNXA7',
         u'mzQxP43Y4A6PfYeArV2mGBEucJfDtsyCk5')

 
.. .. code-block:: bash
..     
..     refill_pass:     <refill wallet password>
..     federation_pass: <federation wallet password>
..     user1_pass:      <user1 password>
..     user2_pass:      <user2 password>
..     user3_pass:      <user3 password>
..     refill_root:     ('', u'mhyCaF2HFk7CVwKmyQ8TahgVdjnHSr1pTv')
..     federation_root: ('', u'mqXz83H4LCxjf2ie8hYNsTRByvtfV43Pa7')
..     user1_root:      ('', u'n36EiKuYYXNS9h84CnkLK3sEevZsfksaGN') -> root address for user1 HD wallet
..     user1_leaf:      ('2015/5/28/9/28/44/982190', u'mjq4rZZEyJGFfzg59RLFmuNJTo3jakEDrS') -> leaf address for user1 HD wallet
..     user2_leaf:      ('2015/5/28/9/28/45/184623', u'mhRJqLG3BwXXG7YADQD3Ng3c6coZVwoFo6') -> leaf address for user2 HD wallet
..     user3_leaf:      ('2015/5/28/9/28/45/387493', u'mhMXXntQCorduhcygY7gLdmuunVEM59C8q') -> leaf address for user3 HD wallet
..     file_hash :      (u'mhXeWEMLnEwVNnyqKrqUDPAYSuwhfyNXA7', u'mzQxP43Y4A6PfYeArV2mGBEucJfDtsyCk5') -> file_hash file_hash+metadata


Federation Wallet Refill
------------------------
Before we can start with spool transactions we need to have a Federation with
all the necessary fuel and tokens.

.. code-block:: python

    >>> from spool import Spool

    >>> spool = Spool(testnet=True)

    >>> # lets refill the federation wallet with necessary fuel*7 and tokens*11 for this example
    >>> txid = spool.refill_main_wallet(refill_root, federation_root[1], 7, 11,
                                        refill_pass, min_confirmations=1, sync=True)
    >>> print txid
    67d22e66ee46a96e94f08bed0c857f23de39aee8b25db5fa0369c495e072e44c

`67d22e66ee46a96e94f08bed0c857f23de39aee8b25db5fa0369c495e072e44c`_

Registrations
-------------

``user1`` registers the master edition
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Now that we have enough funds in the Federation wallet ``user1`` can ascribe
his master edition. A master edition is a register with edition number ``0``
that ascribes the piece to user1 making him the original owner/creator of the
piece. Master editions are ascribed to the user's root address of the HD
wallet.

.. code-block:: python

    >>> # user1 registers the master edition of piece with file_hash
    >>> txid = spool.register(federation_root, user1_root[1], file_hash,
                              federation_pass, 0, min_confirmations=1, sync=True)
    >>> print txid
    f67aa26b5f47e83124040970246c969d04ec9adecc5a97d60754a0f54355ee81

`f67aa26b5f47e83124040970246c969d04ec9adecc5a97d60754a0f54355ee81`_

``user1`` registers the number of editions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Now that ``user1`` has registered the master edition he can now specify how
many editions of the piece will exist. ``user1`` can only do this once and this
cannot be changed in the future. This creates digital scarcity for this
particular piece

.. code-block:: python

    >>> # user1 specifies that there will be 10 editions of the piece with hash file_hash
    >>> txid = spool.editions(federation_root, user1_root, file_hash,
                              federation_pass, 10, min_confirmations=1, sync=True)
    >>> print txid
    f1f2cdf6ef2ee2d8af13f9d45a1fd7700f9f281078c71939f78326a4b6b957dc

`f1f2cdf6ef2ee2d8af13f9d45a1fd7700f9f281078c71939f78326a4b6b957dc`_

``user1`` registers edition number ``1``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Once the number of editions is registered ``user1`` can now start registering
editions so that he can transfer ownership to other users. Each edition is
registered to a different leaf address of ``user1`` HD wallet

.. code-block:: python
    
    >>> # user1 registers edition number 1 of piece with file_hash
    >>> txid = spool.register(federation_root, user1_leaf[1], file_hash,
                              federation_pass, 1, min_confirmations=1, sync=True)
    >>> print txid
    2376a200a326ee7cf87b7fee7ea0f9a80c8b23cc3a0d72732b9a75517e664f23

`2376a200a326ee7cf87b7fee7ea0f9a80c8b23cc3a0d72732b9a75517e664f23`_


Transfers
---------

``user1`` transfers edition number ``1`` to ``user2``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Now that an edition is registered the user can transfer ownership to another
user. Transfering ownserhip implies a transaction originating from ``user1``
wallet address holding the edition. This means that we need to fuel ``user1``
wallet with the necessary funds before performing a spool transaction

.. code-block:: python

    >>> # refill user1 wallet before transfer
    >>> txid = spool.refill(federation_root, user1_leaf[1], 1, 1,
                    federation_pass, min_confirmations=1, sync=True)
    >>> print txid
    45bc2a3eecac9b5538a3b5bc325e94fcffee47c0025e78ece426aeebfac59c24

    >>> # now we can transfer ownserhip of edition 1 from user1 to user2
    >>> txid = spool.transfer(user1_leaf, user2_leaf[1], file_hash,
                              user1_pass, 1, min_confirmations=1, sync=True)
    >>> print txid
    38509a49b00f3c3c3fadedd2c5ce35ffcc05a9737a36dd1b7ff00ed1ffe5fd80

`45bc2a3eecac9b5538a3b5bc325e94fcffee47c0025e78ece426aeebfac59c24`_
`38509a49b00f3c3c3fadedd2c5ce35ffcc05a9737a36dd1b7ff00ed1ffe5fd80`_


Consignments
------------

``user2``  consigns edition number ``1`` to ``user3``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
``user2`` now owns edition ``1`` of piece with hash ``file_hash`` and he can
transfer ownership of the piece. Lets consign the piece to ``user3``

.. code-block:: python
    
    >>> # refill user2 wallet before consign
    >>> txid = spool.refill(federation_root, user2_leaf[1], 1, 1,
                            federation_pass, min_confirmations=1, sync=True)
    >>> print txid
    e07732c8af3557277f68871babc874766c511fdf898449cc9be9e505f8325f10

    >>> # now we can consign edition 1 from user2 to user3
    >>> txid = spool.consign(user2_leaf, user3_leaf[1], file_hash,
                             user2_pass, 1, min_confirmations=1, sync=True)
    >>> print txid
    3b30cea26d49eb023ccd62fb78ddd9308c9505fe0796abc0fe60989980fc5eb8

`e07732c8af3557277f68871babc874766c511fdf898449cc9be9e505f8325f10`_
`3b30cea26d49eb023ccd62fb78ddd9308c9505fe0796abc0fe60989980fc5eb8`_


Unconsignments
--------------

``user3`` unconsigns edition number ``1`` to ``user2``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Now lets unconsign the piece with hash ``file_hash`` back to ``user2``

.. code-block:: python

    >>> # refill user3 wallet before unconsign
    >>> txid = spool.refill(federation_root, user3_leaf[1], 1, 1,
                            federation_pass, min_confirmations=1, sync=True)
    >>> print txid
    f0c9cf0832e7ca14012e7379da35dd2d50bd66df45c2eb089a23b10db4047dcc

    >>> # user3 unconsigns edition number 1 back to user2
    >>> txid = spool.unconsign(user3_leaf, user2_leaf[1], file_hash,
                               user3_pass, 1, min_confirmations=1, sync=True)
    >>> print txid
    11dcb46061526790e0e7cf0a83e9163d35b75461cd203858c1fd7bdb2149db0c

`f0c9cf0832e7ca14012e7379da35dd2d50bd66df45c2eb089a23b10db4047dcc`_
`11dcb46061526790e0e7cf0a83e9163d35b75461cd203858c1fd7bdb2149db0c`_

Loans
-----

``user2`` loans edition number ``1`` to ``user3``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Now that ``user2`` owns the edition again lets loan it to ``user3`` from
15-05-22 to 15-05-23

.. code-block:: python

    >>> # refill user2 wallet before loan
    >>> txid = spool.refill(federation_root, user2_leaf[1], 1, 1,
                            federation_pass, min_confirmations=1, sync=True)
    >>> print txid
    087d85fd421db42c3efac5e6aa499edfe7386101b85314b44c86681a98c27832

    >>> # user2 loans edition number 1 to user3
    >>> txid = spool.loan(user2_leaf, user3_leaf[1], file_hash,
                          user2_pass, 1, '150522', '150523', min_confirmations=1, sync=True)
    >>> print txid
    6cc0066ee737a7104859328729cd10f8c5a5b64be3f4f8bfcab04f8a6aca4c56

`087d85fd421db42c3efac5e6aa499edfe7386101b85314b44c86681a98c27832`_
`6cc0066ee737a7104859328729cd10f8c5a5b64be3f4f8bfcab04f8a6aca4c56`_


.. _67d22e66ee46a96e94f08bed0c857f23de39aee8b25db5fa0369c495e072e44c: https://www.blocktrail.com/tBTC/tx/67d22e66ee46a96e94f08bed0c857f23de39aee8b25db5fa0369c495e072e44c)
.. _f67aa26b5f47e83124040970246c969d04ec9adecc5a97d60754a0f54355ee81: https://www.blocktrail.com/tBTC/tx/f67aa26b5f47e83124040970246c969d04ec9adecc5a97d60754a0f54355ee81
.. _f1f2cdf6ef2ee2d8af13f9d45a1fd7700f9f281078c71939f78326a4b6b957dc: https://www.blocktrail.com/tBTC/tx/f1f2cdf6ef2ee2d8af13f9d45a1fd7700f9f281078c71939f78326a4b6b957dc
.. _2376a200a326ee7cf87b7fee7ea0f9a80c8b23cc3a0d72732b9a75517e664f23: https://www.blocktrail.com/tBTC/tx/2376a200a326ee7cf87b7fee7ea0f9a80c8b23cc3a0d72732b9a75517e664f23
.. _45bc2a3eecac9b5538a3b5bc325e94fcffee47c0025e78ece426aeebfac59c24: https://www.blocktrail.com/tBTC/tx/45bc2a3eecac9b5538a3b5bc325e94fcffee47c0025e78ece426aeebfac59c24
.. _38509a49b00f3c3c3fadedd2c5ce35ffcc05a9737a36dd1b7ff00ed1ffe5fd80: https://www.blocktrail.com/tBTC/tx/38509a49b00f3c3c3fadedd2c5ce35ffcc05a9737a36dd1b7ff00ed1ffe5fd80
.. _e07732c8af3557277f68871babc874766c511fdf898449cc9be9e505f8325f10: https://www.blocktrail.com/tBTC/tx/e07732c8af3557277f68871babc874766c511fdf898449cc9be9e505f8325f10
.. _3b30cea26d49eb023ccd62fb78ddd9308c9505fe0796abc0fe60989980fc5eb8: https://www.blocktrail.com/tBTC/tx/3b30cea26d49eb023ccd62fb78ddd9308c9505fe0796abc0fe60989980fc5eb8
.. _f0c9cf0832e7ca14012e7379da35dd2d50bd66df45c2eb089a23b10db4047dcc: https://www.blocktrail.com/tBTC/tx/f0c9cf0832e7ca14012e7379da35dd2d50bd66df45c2eb089a23b10db4047dcc
.. _11dcb46061526790e0e7cf0a83e9163d35b75461cd203858c1fd7bdb2149db0c: https://www.blocktrail.com/tBTC/tx/11dcb46061526790e0e7cf0a83e9163d35b75461cd203858c1fd7bdb2149db0c
.. _087d85fd421db42c3efac5e6aa499edfe7386101b85314b44c86681a98c27832: https://www.blocktrail.com/tBTC/tx/087d85fd421db42c3efac5e6aa499edfe7386101b85314b44c86681a98c27832
.. _6cc0066ee737a7104859328729cd10f8c5a5b64be3f4f8bfcab04f8a6aca4c56: https://www.blocktrail.com/tBTC/tx/6cc0066ee737a7104859328729cd10f8c5a5b64be3f4f8bfcab04f8a6aca4c56
