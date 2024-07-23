# NFT Contract V2

- [NFT Contract V2](#nft-contract-v2)
  - [Introduction](#introduction)
  - [Usage with Python SDK](#usage-with-python-sdk)
    - [Registration](#registration)
    - [From Existing Contract](#from-existing-contract)
    - [Querying](#querying)
      - [Issuer](#issuer)
      - [Maker](#maker)
      - [Regulator](#regulator)
      - [Unit](#unit)
      - [Is user in the list](#is-user-in-the-list)
      - [Is contract in the list](#is-contract-in-the-list)
    - [Actions](#actions)
      - [Issue](#issue)
      - [Send](#send)
      - [Transfer](#transfer)
      - [Deposit](#deposit)
      - [Withdraw](#withdraw)
      - [Supersede](#supersede)
      - [Add/remove a user from the list](#addremove-a-user-from-the-list)
      - [Add/remove a contract from the list](#addremove-a-contract-from-the-list)

## Introduction
NFT contract V2 adds additional whitelist/blacklist regulation feature upon [NFT contract V1](./nft_ctrt.md).

For the whitelist flavor, only users & contracts included in the list can interact with the NFT contract instance.

For the blacklist flavor, only users & contracts excluded from the list can interact with the NFT contract instance.

## Usage with Python SDK

Examples of NFT contract V2 with whitelist are shown below. The usage of the blacklist one is very similar.

### Registration

```python
import py_vsys as pv

# acnt: pv.Account

# Register a new NFT contract
nc = await pv.NFTCtrtV2Whitelist.register(by=acnt)
print(nc.ctrt_id) # print the id of the newly registered contract
```
Example output

```
CtrtID(CFD6rH5xHXQqweUwAJ3B7J2owvPiKpewsRc)
```

### From Existing Contract

```python
import py_vsys as pv

# ch: pv.Chain

nc_id = "CFD6rH5xHXQqweUwAJ3B7J2owvPiKpewsRc"
nc = pv.NFTCtrtV2Whitelist(ctrt_id=nc_id, chain=ch)
```

### Querying

#### Issuer

The address that has the issuing right of the NFT contract instance.

```python
# nc: pv.NFTCtrtV2Whitelist

print(await nc.issuer)
```
Example output

```
Addr(AU6BNRK34SLuc27evpzJbAswB6ntHV2hmjD)
```

#### Maker
The address that made this NFT contract instance.

```python
# nc: pv.NFTCtrtV2Whitelist

print(await nc.maker)
```
Example output

```
Addr(AU6BNRK34SLuc27evpzJbAswB6ntHV2hmjD)
```

#### Regulator
The address that serves as the regulator of the NFT contract instance.

```python
# nc: pv.NFTCtrtV2Whitelist

print(await nc.regulator)
```
Example output

```
Addr(AU6BNRK34SLuc27evpzJbAswB6ntHV2hmjD)
```

#### Unit
The unit of tokens defined in this NFT contract instance.

As the unit is obviously fixed to 1 for NFTs, the support of querying unit of NFT is for the compatibility with other token-defining contracts.

```python
# nc: pv.NFTCtrtV2Whitelist

print(await nc.unit)
```
Example output

```
1
```

#### Is user in the list
Check if the user is in the whitelist/blacklist

```python
# acnt: pv.Account
# nc: pv.NFTCtrtV2Whitelist

print(await nc.is_user_in_list(acnt.addr.data))
```
Example output

```
False
```

#### Is contract in the list
Check if the user is in the whitelist/blacklist

```python
# nc: pv.NFTCtrtV2Whitelist
arbitrary_ctrt_id = "CF5Zkj2Ycx72WrBnjrcNHvJRVwsbNX1tjgT"

print(await nc.is_ctrt_in_list(arbitrary_ctrt_id))
```
Example output

```
False
```

### Actions

#### Issue
Define a new NFT and issue it. Only the issuer of the contract instance can take this action. The issued NFT will belong to the issuer.

```python
import py_vsys as pv

# issue an NFT without content
# acnt: pv.Account
# nc: pv.NFTCtrtV2Whitelist

resp = await nc.issue(by=acnt)
print(resp)

# issue an NFT with content
# acnt: pv.Account
# nc: pv.NFTCtrtV2Whitelist
# content: str
#
# content json sample:
# {
#	"name": "The name of the NFT",
#	"description": "The description of the NFT",
#	"content": "the url of the image or file",
#	"properties": {},
# }
resp = await nc.issue(by=acnt,content=content)
print(resp)
```
Example output

```
{'type': 9, 'id': 'Cfw93vP2JrKovjbefEh6RDiYNNxcmhBuEspLA6ghU7ws', 'fee': 30000000, 'feeScale': 100, 'timestamp': 1646376022067759104, 'proofs': [{'proofType': 'Curve25519', 'publicKey': '6gmM7UxzUyRJXidy2DpXXMvrPqEF9hR1eAqsmh33J6eL', 'address': 'AU6BNRK34SLuc27evpzJbAswB6ntHV2hmjD', 'signature': '33fMLbFKgAKfD73KcYKmp44WFwDET9NsamviEUwrLhZFeU5H1GdBjqCSt8THWSbt8CFcWCZpaio4jEEcyem3g9z3'}], 'contractId': 'CFD6rH5xHXQqweUwAJ3B7J2owvPiKpewsRc', 'functionIndex': 1, 'functionData': '12Wfh1', 'attachment': ''}
```

#### Send
Send an NFT to another user.

```python
import py_vsys as pv

# acnt0: pv.Account
# acnt1: pv.Account
# nc: pv.NFTCtrtV2Whitelist

resp = await nc.send(
  by=acnt0,
  recipient=acnt1.addr.data,
  tok_idx=0,
)
print(resp)
```
Example output

```
{'type': 9, 'id': 'Ff9SkaBKAN8ZnfrPDYJ7puhcXEJQ1aEdxW2dTWPLVeTN', 'fee': 30000000, 'feeScale': 100, 'timestamp': 1646376182549731072, 'proofs': [{'proofType': 'Curve25519', 'publicKey': '6gmM7UxzUyRJXidy2DpXXMvrPqEF9hR1eAqsmh33J6eL', 'address': 'AU6BNRK34SLuc27evpzJbAswB6ntHV2hmjD', 'signature': '42pSyCh8pRPnLyXBKWwyLvGszeyGaZsf6H7zhgpSE7sbENvoQxMWCbjLAyCf3o2cQNwgE61Jw5U2jj2DvGJKs3TE'}], 'contractId': 'CFD6rH5xHXQqweUwAJ3B7J2owvPiKpewsRc', 'functionIndex': 3, 'functionData': '1bbXGi8m9ZYbKcwaURR5PCByaKR5gBCspa77NqkoRCLMM', 'attachment': ''}
```

#### Transfer
Transfer the ownership of an NFT to another account(e.g. user or contract).
`transfer` is the underlying action of `send`, `deposit`, and `withdraw`. It is not recommended to use transfer directly. Use `send`, `deposit`, `withdraw` instead when possible.

```python
import py_vsys as pv

# acnt0: pv.Account
# acnt1: pv.Account
# nc: pv.NFTCtrtV2Whitelist

resp = await nc.transfer(
  by=acnt1,
  sender=acnt1.addr.data,
  recipient=acnt0.addr.data,
  tok_idx=0,
)
print(resp)
```
Example output

```
{'type': 9, 'id': '1cQqHMHL29faGvbjoZMMptQKUEXiFoTAWsxYriQ7d14', 'fee': 30000000, 'feeScale': 100, 'timestamp': 1646376462540605952, 'proofs': [{'proofType': 'Curve25519', 'publicKey': '4Z7yUcUqa1TcHMPtp7G6XMjxTKuZWXA2hQWNz7X8XsFZ', 'address': 'AU5NsHE8eC2guo3JobD8jrGvnEDQhBP8GtW', 'signature': '2tw9cTJSUie2U6gwAyYkhzXDHr23auMSyYFuAy1NZ6YKuTBH4Em8HeT2Z29tjosNGwuCjhhSiqx3GP1yGtuy35sQ'}], 'contractId': 'CFD6rH5xHXQqweUwAJ3B7J2owvPiKpewsRc', 'functionIndex': 4, 'functionData': '1Xv7sGyd9XHiohkKw3czXTogPULzBESxCD63rpmgaR9RTCPAKj4x9Q1WtWNJ357C1atzoEW81j5BXgQfV9', 'attachment': ''}
```

#### Deposit
Deposit an NFT to a token-holding contract instance(e.g. lock contract).

Note that only the token defined in the token-holding contract instance can be deposited into it.

```python
import py_vsys as pv

# acnt0: pv.Account
# nc: pv.NFTCtrtV2Whitelist
# lc: pv.LockCtrt

lc_id = lc.ctrt_id.data

resp = await nc.deposit(
    by=acnt0,
    ctrt_id=lc_id,
    tok_idx=0,
)
print(resp)
```
Example output

```
{'type': 9, 'id': '9T8d2w6bYEnbawd9ruPQQwwmXz6wHax5f7E9F9LRtWJK', 'fee': 30000000, 'feeScale': 100, 'timestamp': 1646376699813529088, 'proofs': [{'proofType': 'Curve25519', 'publicKey': '6gmM7UxzUyRJXidy2DpXXMvrPqEF9hR1eAqsmh33J6eL', 'address': 'AU6BNRK34SLuc27evpzJbAswB6ntHV2hmjD', 'signature': '5cyu4NxFmaugrQ1tiHL8K5vjsiC6TXrcnDko1VqSFwKcdS6v4Pbgx5ifijRbmuHc3CT7CHDTDyb6FpWfeLxj7KFV'}], 'contractId': 'CFD6rH5xHXQqweUwAJ3B7J2owvPiKpewsRc', 'functionIndex': 5, 'functionData': '1Xv7sHDSN9pKrqwTTbWoYSpThW85PPDaJWpSGeL3sRLWuVySWFuPxzE7ShmweacYLojVHtaKtEYFkPoMyH', 'attachment': ''}
```

#### Withdraw
Withdraw an NFT from a token-holding contract instance(e.g. lock contract).

Note that only the one who deposits the token can withdraw.

```python
import py_vsys as pv

# acnt0: pv.Account
# nc: pv.NFTCtrtV2Whitelist
# lc: pv.LockCtrt

lc_id = lc.ctrt_id.data

resp = await nc.withdraw(
    by=acnt0,
    ctrt_id=lc_id,
    tok_idx=0,
)
print(resp)
```
Example output

```
{'type': 9, 'id': '6SFs4aSaKE8wBepyu2CFaGp8xuK9w16b1ZzannJyy3wu', 'fee': 30000000, 'feeScale': 100, 'timestamp': 1646376742474464000, 'proofs': [{'proofType': 'Curve25519', 'publicKey': '6gmM7UxzUyRJXidy2DpXXMvrPqEF9hR1eAqsmh33J6eL', 'address': 'AU6BNRK34SLuc27evpzJbAswB6ntHV2hmjD', 'signature': '4MfsYA7nPVt8B5BYS2KQMZKFMKxneAQctyyBdwmCSrUDsiVgrq1TqKMH7ZvuyreiaAom7L8QJnAWwCJp6MiRAduh'}], 'contractId': 'CFD6rH5xHXQqweUwAJ3B7J2owvPiKpewsRc', 'functionIndex': 6, 'functionData': '1Y5SePVHvc7suviTeugUSVB5XYLtM4XJtmzY3yuqEUR3Hw7XBSFQcLYyvLDGb2cdGE5ifAgnirzhc7QTTV', 'attachment': ''}
```

#### Supersede
Transfer the issuer & regulator role of the contract to a new user.

Note that only the contract maker has the privilege to take this action.

```python
import py_vsys as pv

# acnt0: pv.Account
# acnt1: pv.Account
# acnt2: pv.Account
# nc: pv.NFTCtrtV2Whitelist

resp = await nc.supersede(
    by=acnt0,
    new_issuer=acnt1.addr.data,
    new_regulator=acnt2.addr.data,
)
print(resp)
```
Example output

```
{'type': 9, 'id': 'bZBmESBWbefKDhVEjVyqqS2EAU5S59ucUWrJEAJUuec', 'fee': 30000000, 'feeScale': 100, 'timestamp': 1646376831198232064, 'proofs': [{'proofType': 'Curve25519', 'publicKey': '6gmM7UxzUyRJXidy2DpXXMvrPqEF9hR1eAqsmh33J6eL', 'address': 'AU6BNRK34SLuc27evpzJbAswB6ntHV2hmjD', 'signature': '91wKK871gPUxcmwmQzZiZQ2UNUTDNFvbnKAAdCc4g5GqNpJ912UNXT9kRzWrzztJitFLVhkEGi7YUo6RURp3FmY'}], 'contractId': 'CFD6rH5xHXQqweUwAJ3B7J2owvPiKpewsRc', 'functionIndex': 0, 'functionData': '1iSib21mKY5QhoPcoPYTNqwSv8VaM5AN4wzmCcod4q7P4NEy1A7sr4j4F6tfxVkycuJifHWcLMR', 'attachment': ''}
```

#### Add/remove a user from the list
Add/remove a user from the whitelist/blacklist.

Note the regulator has the privilege to take this action.

```python
import py_vsys as pv

# acnt0: pv.Account
# acnt1: pv.Account
# nc: pv.NFTCtrtV2Whitelist

resp = await nc.update_list_user(
    by=acnt0,
    addr=acnt1.addr.data,
    val=True, # False to remove
)
print(resp)
```
Example output

```
{'type': 9, 'id': '8j9fAfG4oUG5mRxyRpW6yGH76ouMHrQeMgujyiYAjLx', 'fee': 30000000, 'feeScale': 100, 'timestamp': 1646377488444199936, 'proofs': [{'proofType': 'Curve25519', 'publicKey': '6gmM7UxzUyRJXidy2DpXXMvrPqEF9hR1eAqsmh33J6eL', 'address': 'AU6BNRK34SLuc27evpzJbAswB6ntHV2hmjD', 'signature': '5Ket2nDXyWXpChw13ecWhMejGGDPa4uK1DhbNBGK4wgp5sDiaQZbEczpsaRzHUuM2DhCZCi6AnfsJaeL6Yed4Yet'}], 'contractId': 'CFD6rH5xHXQqweUwAJ3B7J2owvPiKpewsRc', 'functionIndex': 2, 'functionData': '1QLRyUKuvAg1foWyW4NLRc14fe8HLzgbs9ZeHYNK2', 'attachment': ''}
```

#### Add/remove a contract from the list
Add/remove a contract from the whitelist/blacklist.

Note the regulator has the privilege to take this action.

```python
import py_vsys as pv

# acnt0: pv.Account
# acnt1: pv.Account
# nc: pv.NFTCtrtV2Whitelist

arbitrary_ctrt_id = "CF5Zkj2Ycx72WrBnjrcNHvJRVwsbNX1tjgT"

resp = await nc.update_list_ctrt(
    by=acnt0,
    addr=arbitrary_ctrt_id,
    val=True, # False to remove
)
print(resp)
```
Example output

```
{'type': 9, 'id': '4i8zPhUnMbhvVRC6jHfF8dmKUsj1VNRxbYboKNSXArSv', 'fee': 30000000, 'feeScale': 100, 'timestamp': 1646377716126999040, 'proofs': [{'proofType': 'Curve25519', 'publicKey': '6gmM7UxzUyRJXidy2DpXXMvrPqEF9hR1eAqsmh33J6eL', 'address': 'AU6BNRK34SLuc27evpzJbAswB6ntHV2hmjD', 'signature': '5cHgE1yKT43QBTrCerD4cH45JdKbuC7Ec7cBP1X19KBfKrVvnEQGzymmAjkPNp2PfiCbrNz4Fkuvx9cEGydkD2ng'}], 'contractId': 'CFD6rH5xHXQqweUwAJ3B7J2owvPiKpewsRc', 'functionIndex': 2, 'functionData': '1QWyS5TmAbHA8jyaykmqtcJz5oezpMiXGSM4JZMyJ', 'attachment': ''}
```
