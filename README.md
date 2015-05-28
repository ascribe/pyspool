# pyspool
pyspool is a reference implementation of the Secure Public Online Ownership Ledger 
[SPOOL](https://github.com/ascribe/spool) and part of the development stack of [ascribe.io](https://www.ascribe.io/)

## Install
```
pip install -r requirements.txt
python setup.py install
```

## Overview
All hashes are in base 58 so that they can be inserted in the blockchain

##### Refill Wallet
The refill wallet is only used to refill the Federation Wallet with 10000 and 600 satoshi outputs.
This way we maintain the Federation Wallet clean which makes it easier to manage.

##### Federation Wallet
The Federation wallet is the wallet from where all the registers in the blockchain occur.
We can check the validity of transactions by looking at the origin of this transactions and
see if the originating address belongs to a federation. For instance all pieces registered through
[ascribe.io](https://www.ascribe.io/) will originate from the address `1JttRRdtAi6cDNM23Uq4BEU61R8kJeANJs` 
for the first version of the protocol or `1AScRhqdXMrJyxNmjEapMZi1PLFsqmLquG` for protocol version `01`.

The Federation wallet should only contain fuel outputs with the amount of 10000 satoshi and token outputs
with the amount of 600 satoshi. The fuel is used to pay the fee for the transactions and tokens are used
to register address on the blockchain.

Ensuring that the Federation wallet cointains outputs with these amounts makes the transactions simpler 
since there is no need for change. It is also easier to keep track of the unspents in order to prevent 
invalid transactions due to double spends (specially important when there is a high throughput of 
transactions).

## Example
All the addresses and transaction ids outputed by this examples can be checked in the blockchain.

```
For this example we will be implementing the following actions:

1. Refill Federation wallet with fuel and tokens
2. user1 registers master edition
3. user1 registers number of editions
4. user1 registers edition number 1
5. user1 transferes edition number 1 to user2
6. user2 consigns edition number 1 to user 3
7. user3 unconsigns edition number 1 to user2
8. user2 loans edition number 1 to user 3

This is the information that we will need:
refill_pass:     <refill wallet password>
federation_pass: <federation wallet password>
user1_pass:      <user1 password>
user2_pass:      <user2 password>
user3_pass:      <user 3 password>
refill_root:     ('', u'mhyCaF2HFk7CVwKmyQ8TahgVdjnHSr1pTv')
federation_root: ('', u'mqXz83H4LCxjf2ie8hYNsTRByvtfV43Pa7')
user1_root:      ('', u'n36EiKuYYXNS9h84CnkLK3sEevZsfksaGN') -> root address for user1 HD wallet
user1_leaf:      ('2015/5/28/9/28/44/982190', u'mjq4rZZEyJGFfzg59RLFmuNJTo3jakEDrS') -> leaf address for user1 HD wallet
user2_leaf:      ('2015/5/28/9/28/45/184623', u'mhRJqLG3BwXXG7YADQD3Ng3c6coZVwoFo6') -> leaf address for user2 HD wallet
user3_leaf:      ('2015/5/28/9/28/45/387493', u'mhMXXntQCorduhcygY7gLdmuunVEM59C8q') -> leaf address for user3 HD wallet
file_hash :      (u'mhXeWEMLnEwVNnyqKrqUDPAYSuwhfyNXA7', u'mzQxP43Y4A6PfYeArV2mGBEucJfDtsyCk5') -> file_hash file_hash+metadata
```

Before we can start with spool transactions we need to have a Federation
with all the necessary fuel and tokens.
```python
from spool import Spool

spool = Spool(testnet=True)

# lets refill the federation wallet with necessary fuel*7 and tokens*11 for this example
txid = spool.refill_main_wallet(refill_root, federation_root[1], 7, 11,
                                refill_pass, min_confirmations=1, sync=True)
print txid
67d22e66ee46a96e94f08bed0c857f23de39aee8b25db5fa0369c495e072e44c
```
[67d22e66ee46a96e94f08bed0c857f23de39aee8b25db5fa0369c495e072e44c](https://www.blocktrail.com/tBTC/tx/67d22e66ee46a96e94f08bed0c857f23de39aee8b25db5fa0369c495e072e44c)

Now that we have enough funds in the Federation wallet user1 can ascribe its master edition.
A master edition its a register with edition number 0 that ascribes the piece to user1 making him the
original owner/creator of the piece. Master editions are ascribed to the user's root address of the HD wallet
```python
# user1 registers the master edition of piece with file_hash
txid = spool.register(federation_root, user1_root[1], file_hash,
                      federation_pass, 0, min_confirmations=1, sync=True)
print txid
f67aa26b5f47e83124040970246c969d04ec9adecc5a97d60754a0f54355ee81
```
[f67aa26b5f47e83124040970246c969d04ec9adecc5a97d60754a0f54355ee81](https://www.blocktrail.com/tBTC/tx/f67aa26b5f47e83124040970246c969d04ec9adecc5a97d60754a0f54355ee81)

Now that user1 has registered the master edition he can now specify how many editions of the piece will exist.
user1 can only do this once and this cannot be changed in the future. This creates digital scarcity for this 
particular piece
```python
# user1 specifies that there will be 10 editions of the piece with hash file_hash
txid = spool.editions(federation_root, user1_root, file_hash,
                      federation_pass, 10, min_confirmations=1, sync=True)
print txid
f1f2cdf6ef2ee2d8af13f9d45a1fd7700f9f281078c71939f78326a4b6b957dc
```
[f1f2cdf6ef2ee2d8af13f9d45a1fd7700f9f281078c71939f78326a4b6b957dc](https://www.blocktrail.com/tBTC/tx/f1f2cdf6ef2ee2d8af13f9d45a1fd7700f9f281078c71939f78326a4b6b957dc)

Once the number of editions is registered user1 can now start registering editions so that he can
transfer ownership to other users. Each edition is registered to a different leaf address of user1 
HD wallet
```python
# user1 registers edition number 1 of piece with file_hash
txid = spool.register(federation_root, user1_leaf[1], file_hash,
                      federation_pass, 1, min_confirmations=1, sync=True)
print txid
2376a200a326ee7cf87b7fee7ea0f9a80c8b23cc3a0d72732b9a75517e664f23
```
[2376a200a326ee7cf87b7fee7ea0f9a80c8b23cc3a0d72732b9a75517e664f23](https://www.blocktrail.com/tBTC/tx/2376a200a326ee7cf87b7fee7ea0f9a80c8b23cc3a0d72732b9a75517e664f23)

Now that and edition is registered the user can transfer ownership to another user.
Transfering ownserhip implies a transaction originating from user1 wallet address holding the edition. 
This means that we need to fuel user1 wallet with the necessary funds before performing a spool 
transaction
```python
# refill user1 wallet before transfer
txid = spool.refill(federation_root, user1_leaf[1], 1, 1,
                    federation_pass, min_confirmations=1, sync=True)
print txid
45bc2a3eecac9b5538a3b5bc325e94fcffee47c0025e78ece426aeebfac59c24

# now we can transfer ownserhip of edition 1 from user1 to user2
txid = spool.transfer(user1_leaf, user2_leaf[1], file_hash,
                      user1_pass, 1, min_confirmations=1, sync=True)
print txid
38509a49b00f3c3c3fadedd2c5ce35ffcc05a9737a36dd1b7ff00ed1ffe5fd80
```
[45bc2a3eecac9b5538a3b5bc325e94fcffee47c0025e78ece426aeebfac59c24](https://www.blocktrail.com/tBTC/tx/45bc2a3eecac9b5538a3b5bc325e94fcffee47c0025e78ece426aeebfac59c24)
[38509a49b00f3c3c3fadedd2c5ce35ffcc05a9737a36dd1b7ff00ed1ffe5fd80](https://www.blocktrail.com/tBTC/tx/38509a49b00f3c3c3fadedd2c5ce35ffcc05a9737a36dd1b7ff00ed1ffe5fd80)

User2 now owns edition 1 of piece with hash file_hash and he can transfer ownership of the piece.
Lets consign the piece to user3
```python
# refill user2 wallet before consign
txid = spool.refill(federation_root, user2_leaf[1], 1, 1,
                    federation_pass, min_confirmations=1, sync=True)
print txid
e07732c8af3557277f68871babc874766c511fdf898449cc9be9e505f8325f10

# now we can consign edition 1 from user2 to user3
txid = spool.consign(user2_leaf, user3_leaf[1], file_hash,
                     user2_pass, 1, min_confirmations=1, sync=True)
print txid
3b30cea26d49eb023ccd62fb78ddd9308c9505fe0796abc0fe60989980fc5eb8
```
[e07732c8af3557277f68871babc874766c511fdf898449cc9be9e505f8325f10](https://www.blocktrail.com/tBTC/tx/e07732c8af3557277f68871babc874766c511fdf898449cc9be9e505f8325f10)
[3b30cea26d49eb023ccd62fb78ddd9308c9505fe0796abc0fe60989980fc5eb8](https://www.blocktrail.com/tBTC/tx/3b30cea26d49eb023ccd62fb78ddd9308c9505fe0796abc0fe60989980fc5eb8)

Now lets unconsign the piece with hash file_hash back to user2
```python
# refill user3 wallet before unconsign
txid = spool.refill(federation_root, user3_leaf[1], 1, 1,
                    federation_pass, min_confirmations=1, sync=True)
print txid
f0c9cf0832e7ca14012e7379da35dd2d50bd66df45c2eb089a23b10db4047dcc

# user3 unconsigns edition number 1 back to user2
txid = spool.unconsign(user3_leaf, user2_leaf[1], file_hash,
                       user3_pass, 1, min_confirmations=1, sync=True)
print txid
11dcb46061526790e0e7cf0a83e9163d35b75461cd203858c1fd7bdb2149db0c
```
[f0c9cf0832e7ca14012e7379da35dd2d50bd66df45c2eb089a23b10db4047dcc](https://www.blocktrail.com/tBTC/tx/f0c9cf0832e7ca14012e7379da35dd2d50bd66df45c2eb089a23b10db4047dcc)
[11dcb46061526790e0e7cf0a83e9163d35b75461cd203858c1fd7bdb2149db0c](https://www.blocktrail.com/tBTC/tx/11dcb46061526790e0e7cf0a83e9163d35b75461cd203858c1fd7bdb2149db0c)

Now that user2 owns the edition again lets loan it to user3 from 15-05-22 to 15-05-23
```python
# refill user2 wallet before loan
txid = spool.refill(federation_root, user2_leaf[1], 1, 1,
                    federation_pass, min_confirmations=1, sync=True)
print txid
087d85fd421db42c3efac5e6aa499edfe7386101b85314b44c86681a98c27832

# user2 loans edition number 1 to user3
txid = spool.loan(user2_leaf, user3_leaf[1], file_hash,
                  user2_pass, 1, '150522', '150523', min_confirmations=1, sync=True)
print txid
6cc0066ee737a7104859328729cd10f8c5a5b64be3f4f8bfcab04f8a6aca4c56
```
[087d85fd421db42c3efac5e6aa499edfe7386101b85314b44c86681a98c27832](https://www.blocktrail.com/tBTC/tx/087d85fd421db42c3efac5e6aa499edfe7386101b85314b44c86681a98c27832)
[6cc0066ee737a7104859328729cd10f8c5a5b64be3f4f8bfcab04f8a6aca4c56](https://www.blocktrail.com/tBTC/tx/6cc0066ee737a7104859328729cd10f8c5a5b64be3f4f8bfcab04f8a6aca4c56)

## Documentation

##### Spool(testnet=False)
Class that contains all Spool methods.

    In the SPOOL implementation there is no notion of users only addresses.
    All addresses come from BIP32 HD wallets. This makes it easier to manage all the keys
    since we can retrieve everything we need from a master secret (namely the private key
    to sign the transactions).

    Since we are dealing with HD wallets we expect all from_address to be a tuple of 
    (path, address) so that we can retrieve the private key for that particular 
    leaf address.
    If we want to use the root address we can just pass an empty string to the 
    first element of the tuple e.g. ('', address). For instance when using the 
    federation wallet address we have no need to create leaf addresses.

    A file is represented by two hashes:
        - file_hash: is the hash of the digital file
        - file_hash_metadata: is the hash of the digital file + metadata
    The hash is passed to the methods has a tuple (file_hash, file_hash_metadata)
- **`testnet`**: Whether to use the bitcoin testnet or mainnet. Defaults to False
- **`returns`**: Spool instance

##### Spool.register(from_address, to_address, hash, password, edition_num, min_confirmations=6, sync=False)
Register an edition or master edition of a piece
- **`from_address`**: Federation address. All register transactions originate from the the Federation wallet
- **`to_address`**: Address registering the edition
- **`hash`**: Hash of the piece. Tuple (file_hash, file_hash_metadata)
- **`password`**: Federation wallet password. For signing the transaction
- **`edition_num`**: The number of the edition to register. User edition_num=0 to register the master edition
- **`min_confirmations`**: Number of confirmations when chosing the inputs of the transaction. Defaults to 6
- **`sync`**: Perform the transaction in synchronous mode, the call to the function will block until there is at
        least on confirmation on the blockchain. Defaults to False
- **`returns`**: transaction id

##### Spool.editions(from_address, to_address, hash, password, num_editions, min_confirmations=6, sync=False)
Register the number of editions of a piece
- **`from_address`**: Federation address. All register transactions originate from the the Federation wallet
- **`to_address`**: Address registering the number of editions
- **`hash`**: Hash of the piece. Tuple (file_hash, file_hash_metadata)
- **`password`**: Federation wallet password. For signing the transaction
- **`num_editions`**: Number of editions of the piece
- **`min_confirmations`**: Number of confirmations when chosing the inputs of the transaction. Defaults to 6
- **`sync`**: Perform the transaction in synchronous mode, the call to the function will block until there is at
        least on confirmation on the blockchain. Defaults to False
- **`returns`**: transaction id

##### Spool.transfer(from_address, to_address, hash, password, edition_num, min_confirmations=6, sync=False)
Transfer a piece between addresses
- **`from_address`**: Address currently owning the edition
- **`to_address`**: Address to receive the edition
- **`hash`**: Hash of the piece. Tuple (file_hash, file_hash_metadata)
- **`password`**: Password for the wallet currently owning the edition. For signing the transaction
- **`edition_num`**: the number of the edition to transfer
- **`min_confirmations`**: Number of confirmations when chosing the inputs of the transaction. Defaults to 6
- **`sync`**: Perform the transaction in synchronous mode, the call to the function will block until there is at
        least on confirmation on the blockchain. Defaults to False
- **`returns`**: transaction id

##### Spool.consign(from_address, to_address, hash, password, edition_num, min_confirmations=6, sync=False)
Consign a piece to an address
- **`from_address`**: Address currently owning the edition
- **`to_address`**: Address to where the piece will be consigned to
- **`hash`**: Hash of the piece. Tuple (file_hash, file_hash_metadata)
- **`password`**: Password for the wallet currently owning the edition. For signing the transaction
- **`edition_num`**: the number of the edition to consign
- **`min_confirmations`**: Number of confirmations when chosing the inputs of the transaction. Defaults to 6
- **`sync`**: Perform the transaction in synchronous mode, the call to the function will block until there is at
        least on confirmation on the blockchain. Defaults to False
- **`returns`**: transaction id

##### Spool.unconsign(from_address, to_address, hash, password, edition_num, min_confirmations=6, sync=False)
Unconsign the edition
- **`from_address`**: Address where the edition is currently consigned
- **`to_address`**: Address that consigned the piece to _from_address_
- **`hash`**: Hash of the piece. Tuple (file_hash, file_hash_metadata)
- **`password`**: Password for the wallet currently holding the edition. For signing the transaction
- **`edition_num`**: the number of the edition to unconsign
- **`min_confirmations`**: Number of confirmations when chosing the inputs of the transaction. Defaults to 6
- **`sync`**: Perform the transaction in synchronous mode, the call to the function will block until there is at
        least on confirmation on the blockchain. Defaults to False
- **`returns`**: transaction id

##### Spool.loan(from_address, to_address, hash, password, edition_num, loan_start, loan_end, min_confirmations=6, sync=False)
Loan the edition
- **`from_address`**: Address currently holding the edition
- **`to_address`**: Address to loan the edition to
- **`hash`**: Hash of the piece. Tuple (file_hash, file_hash_metadata)
- **`password`**: Password for the wallet currently holding the edition. For signing the transaction
- **`edition_num`**: the number of the edition to unconsign
- **`loan_start`**: Start date for the loan. In the form `YYMMDD`
- **`loan_end`**: End date for the loan. In the form `YYMMDD`
- **`min_confirmations`**: Number of confirmations when chosing the inputs of the transaction. Defaults to 6
- **`sync`**: Perform the transaction in synchronous mode, the call to the function will block until there is at
        least on confirmation on the blockchain. Defaults to False
- **`returns`**: transaction id

##### Spool.refill_main_wallet(from_address, to_address, nfees, ntokens, password, min_confirmations=6, sync=False)
Refill the Federation wallet with tokens and fees. This keeps the federation wallet clean.
Dealing with exact values simplifies the transactions. No need to calculate change. Easier to keep track of the
unspents and prevent double spends that would result in transactions being rejected by the bitcoin network.
- **`from_address`**: Refill wallet address. Refills the federation wallet with tokens and fees
- **`to_address`**: Federation wallet address
- **`nfees`**: Number of fees to transfer. Each fee is 10000 satoshi. Used to pay for the transactions
- **`ntokens`**: Number of tokens to transfer. Each token is 600 satoshi. Used to register hashes in the blockchain
- **`password`**: Password for the Refill wallet. Used to sign the transaction
- **`min_confirmations`**: Number of confirmations when chosing the inputs of the transaction. Defaults to 6
- **`sync`**: Perform the transaction in synchronous mode, the call to the function will block until there is at
        least on confirmation on the blockchain. Defaults to False
- **`returns`**: transaction id

##### Spool.refill(from_address, to_address, nfees, ntokens, edition_num, min_confirmations=6, sync=False)
Refill wallets with the necessary fuel to perform spool transactions
- **`from_address`**: Federation wallet address. Fuels the wallets with tokens and fees. All transactions to wallets
                holding a particular piece should come from the Federation wallet
- **`to_address`**: Wallet address that needs to perform a spool transaction
- **`nfees`**: Number of fees to transfer. Each fee is 10000 satoshi. Used to pay for the transactions
- **`ntokens`**: Number of tokens to transfer. Each token is 600 satoshi. Used to register hashes in the blockchain
- **`password`**: Password for the Federation wallet. Used to sign the transaction
- **`min_confirmations`**: Number of confirmations when chosing the inputs of the transaction. Defaults to 6
- **`sync`**: Perform the transaction in synchronous mode, the call to the function will block until there is at
        least on confirmation on the blockchain. Defaults to False
- **`returns`**: transaction id

##### Spool.simple_spool_transaction(from_address, to, op_return, min_confirmations=6)
Utililty function to create the spool transactions. Selects the inputs, encodes the op_return and
constructs the transaction.
- **`from_address`**: Address originating the the transaction
- **`to`**: list of addresses to receive tokens (file_hash, file_hash_metadata, ...)
- **`op_return`**: String representation of the spoolverb, as returned by the properties of Spoolverb
- **`min_confirmations`**: Number of confirmations when chosing the inputs of the transaction. Defaults to 6
- **`returns`**: unsigned transaction

##### _exception_ Spool.SpoolFundsError(message)
Exception raised when there are not enough funds in a wallet to perform a transaction

##### File(filename, testnet=False, **kwargs)
Returns a instance of File given the file name.
This class is used to calculate the hash of file and the hash of the file + metadata
to be included on the blockchain
- **`filename`**: Name of the file
- **`testnet`**: Whether to use the bitcoin testnet or mainnet. Defaults to False
- **`kwargs`**: Additional optional metadata to be encoded with the file.
          e.g. `{'title': 'piece title', 'artist_name': 'artist'}`
- **`returns`**: File instance

##### File.from_hash(hash)
Returns an instance of File given the hash of the file.
- **`hash`**: hash of the file
- **`returns`**: File instance

##### _attribute_ File.file_hash
Attribute with the hash of the file

##### _attribute_ File.file_hash_metadata
Attribute with the hash of the file + metadata

##### Wallet(password, testnet=False)
Create a Hierarchical Determistic (HD) wallet. Addresses return by the wallet are of the form (path, address)
- **`password`**: master secret for the wallet
- **`testnet`**: Whether to use the bitcoin testnet or mainnet. Defaults to False
- **`returns`**: Wallet instance

##### Wallet.address_from_path(path=None)
- **`path`**: path for the HD wallet. If path is None it will generate a unique path based on time
- **`returns`**: a tuple with the path and leaf address

##### _attribute_ Wallet.root_address
Attribute with the root address of the HD Wallet

##### Spoolverb(num_editions=None, edition_num=None, loan_start='',loan_end='', meta='ASCRIBESPOOL', version='01', action=None)
Allows for easy creation of the verb to be encoded on the op_return of all SPOOL transactions
- **`num_editions`**: number of editions to register
- **`edition_num`**: number of the edition to use
- **`loan_start`**: start of the loan in the format YYMMDD
- **`loan_end`**: end of the loan in the format YYMMDD
- **`meta`**: Header for the spool protocol. Defaults to 'ASCRIBESPOOL'
- **`version`**: Version of the protocol. Defaults to '01'
- **`action`**: one of the actions in supported_actions
- **`returns`**: an instance of Spoolverb

##### Spoolverb.from_verb(verb)
Construct a Spoolverb instance from the string representation of the verb
- **`verb`**: string representation of the verb e.g. `ASCRIBESPOOL01LOAN12/150526150528`
- **`returns`**: Spoolverb instance

##### _property_ Spoolverb.register
- **`returns`**: string representation of the _REGISTER_ spoolverb e.g. `ASCRIBESPOOL01REGISTER1`

##### _property_ Spoolverb.editions
- **`returns`**: string representation of the _EDITIONS_ spoolverb e.g. `ASCRIBESPOOL01EDITIONS10`

##### _property_ Spoolverb.transfer
- **`returns`**: string representation of the _TRANSFER_ spoolverb e.g. `ASCRIBESPOOL01TRANSFER1`

##### _property_ Spoolverb.consign
- **`returns`**: string representation of the _CONSIGN_ spoolverb e.g. `ASCRIBESPOOL01CONSIGN1`

##### _property_ Spoolverb.unconsign
- **`returns`**: string representation of the _UNCONSIGN_ spoolverb e.g. `ASCRIBESPOOL01UNCOSIGN1`

##### _property_ Spoolverb.loan
- **`returns`**: string representation of the _LOAN_ spoolverb e.g. `ASCRIBESPOOL01LOAN1/150526150528`

##### _property_ Spoolverb.fuel
- **`returns`**: string representation og the _FUEL_ spoolverb e.g. `ASCRIBESPOOL01FUEL`

##### _exception_ SpoolverbError(message)
Exception to be raised when a invalid or malformed spoolverb is encountered

##### BlockchainSpider(testnet=False)
Spool blockain explorer. Retrieves from the blockchain the chain of ownership 
of a hash created with the SPOOL protocol
- **`testnet`**: Whether to use the bitcoin testnet or mainnet. Defaults to False
- **`returns`**: BlockainSpider instance

##### BlockchainSpider.history(hash)
Retrieve the ownership tree of all editions of a piece given the hash
- **`hash`**: Hash of the file to check. Can be created with the File class
- **`returns`**: ownsership tree of all editions of a piece

##### BlockchainSpider.chain(ownership_tree, edition_number)
- **`ownership_tree`**: ownsership tree of all editions of a piece
- **`edition_number`**: The edition number to check for
- **`returns`**: The chain of ownsership of a particular edition of the piece ordered by timestamp
           on the blockchain

##### BlockchainSpider.strip_loan(chain)
Returns the chain without loan. This way we can look at the last transaction 
to establish ownership
- **`chain`**: chain for a particular edition
- **`returns`**: chain with loan transactions striped from the end of the chain

##### BlockchainSpider.pprint(ownership_tree)
Utility function to pretty print the ownership tree of a piece
- **`ownsership_tree`**: Ownership tree of a piece
- **`returns`**: None

##### BlockchainSpider.decode_op_return(op_return_hex)
Decodes the op_return hex representation into a string
- **`op_return_hex`**: hex representation of the op_return
- **`returns`**: string representation of the op_return

##### BlockchainSpider.check_script(vouts)
Looks into the vouts list of a transaction and returns the op_return if one exists
- **`vouts`**: lists of outputs of a transaction
- **`returns`**: string representation of the op_return

##### Ownsership(address, piece_address, edition_number, testnet=False)
Checks the actions that an address can make on a piece.
- **`address`**: bitcoin address to check ownership over piece_address
- **`piece_address`**: bitcoin address of the piece to check
- **`edition_number`**: the edition number of the piece
- **`testnet`**: testnet flag. Defaults to false
- **`returns`**: returns an instance of the Ownserhip class

##### _property_ Ownsership.can_register_master
- **`returns`**: True if _address_ can register the master edition of _piece_address_ else False

##### _property_ Ownsership.can_editions
- **`returns`**: True if _address_ can register the number of editions of _piece_address_ else False

##### _property_ Ownsership.can_register
- **`returns`**: True if _address_ can register the edition _edition_number_ of _piece_address_ else False

##### _property_ Ownsership.can_transfer
- **`returns`**: True if _address_ can transfer the edition _edition_number_ of _piece_address_ else False

##### _property_ Ownsership.can_consign
- **`returns`**: True if _address_ can consign the edition _edition_number_ of _piece_address_ else False

##### _property_ Ownsership.can_unconsign
- **`returns`**: True if _address_ can unconsign the edition _edition_number_ of _piece_address_ else False

##### _property_ Ownsership.can_loan
- **`returns`**: True if _address_ can loan the edition _edition_number_ of _piece_address_ else False

##### _attribute_ Ownserhip.reason
Attribute set with a reason message when one the above properties returns `False`

##### _exception_ Ownership.OwnsershipError(message)
Exception to be raised when an address does not have permissions to perform an action on a piece

## Testing
Run tests that require no transactions to be made in the bitcoin network
```bash
python -m unittest discover -v tests/
```

To run the tests for the spool protocol you need to provide the _REFILL_ and _FEDERATION_ 
wallet passwords. Note that these tests may take some time since we need to wait for the 
bitcoin networ to confirm each transaction
```bash
TEST_SPOOL=1 TEST_REFILL_PASS=<refill_pass> TEST_FEDERATION_PASS=<federation_pass> python -m unittest discover -v tests/
```

## Contributing
Pull requests, feedback, suggestions are welcome.

<rodolphe@ascribe.io>

## Background
This was developed by ascribe GmbH as part of the overall ascribe technology stack. http://www.ascribe.io

## Copyright

This code is © 2015 ascribe GmbH.

This code is available for use under the [Creative Commons CC-BY-SA 3.0 license](https://creativecommons.org/licenses/by-sa/3.0/). 