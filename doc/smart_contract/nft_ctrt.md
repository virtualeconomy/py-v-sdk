# NFT Contract V1

- [NFT Contract V1](#nft-contract-v1)
  - [Introduction](#introduction)
  - [Usage with Python SDK](#usage-with-python-sdk)
    - [Registration](#registration)
    - [From Existing Contract](#from-existing-contract)
    - [Querying](#querying)
      - [Issuer](#issuer)
      - [Maker](#maker)
      - [Unit](#unit)
    - [Actions](#actions)
      - [Issue](#issue)
      - [Send](#send)
      - [Transfer](#transfer)
      - [Deposit](#deposit)
      - [Withdraw](#withdraw)
      - [Supersede](#supersede)


## Introduction

NFT contract supports defining & managing [NFTs(Non-Fungible Tokens)](https://en.wikipedia.org/wiki/Non-fungible_token).
NFT can be thought of as a special kind of custom token where
- The unit is fixed to 1 and cannot be updated
- The max issuing amount for a kind of token is fixed to 1.

Note that a NFT contract instance on the VSYS blockchain supports defining multiple NFTs (unlike Token contact which supports defining only 1 kind of token per contract instance).

## Usage with Python SDK

### Registration

```python
import py_vsys as pv

# acnt: pv.Account

# Register a new NFT contract
nc = await pv.NFTCtrt.register(by=acnt)
print(nc.ctrt_id) # print the id of the newly registered contract
```
Example output

```
CtrtID(CEu8AuKJS2Pr67RPV9dFjPAb8TL151weQsi)
```

### From Existing Contract

```python
import py_vsys as pv

# ch: pv.Chain

nc_id = "CEu8AuKJS2Pr67RPV9dFjPAb8TL151weQsi"
nc = pv.NFTCtrt(ctrt_id=nc_id, chain=ch)
```

### Querying

#### Issuer

The address that has the issuing right of the NFT contract instance.

```python
# nc: pv.NFTCtrt

print(await nc.issuer)
```
Example output

```
Addr(AU6BNRK34SLuc27evpzJbAswB6ntHV2hmjD)
```

#### Maker
The address that made this NFT contract instance.

```python
# nc: pv.NFTCtrt

print(await nc.maker)
```
Example output

```
Addr(AU6BNRK34SLuc27evpzJbAswB6ntHV2hmjD)
```

#### Unit
The unit of tokens defined in this NFT contract instance.

As the unit is obviously fixed to 1 for NFTs, the support of querying unit of NFT is for the compatibility with other token-defining contracts.

```python
# nc: pv.NFTCtrt

print(await nc.unit)
```
Example output

```
1
```

### Actions

#### Issue
Define a new NFT and issue it. Only the issuer of the contract instance can take this action. The issued NFT will belong to the issuer.

```python
import py_vsys as pv

# issue an NFT without content
# acnt: pv.Account
# nc: pv.NFTCtrt

resp = await nc.issue(by=acnt)
print(resp)

# issue an NFT with content
# acnt: pv.Account
# nc: pv.NFTCtrt
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
{'type': 9, 'id': 'DyFKAkv6xSWuPjau3k8YXoPG4Awk2DL1iCK62Tch8k9u', 'fee': 30000000, 'feeScale': 100, 'timestamp': 1642064271931793920, 'proofs': [{'proofType': 'Curve25519', 'publicKey': '6gmM7UxzUyRJXidy2DpXXMvrPqEF9hR1eAqsmh33J6eL', 'address': 'AU6BNRK34SLuc27evpzJbAswB6ntHV2hmjD', 'signature': '5bVP3Krrddg8Z5J2XDcKb8MHfjqdhhFH6S3rh1pnj2wJde8YsatkBLHhyUs5f4LgqJHKK1zYVaUpdzF5Py2xUS27'}], 'contractId': 'CEvfK7Jw8ZxnbxZjEW8Ejumco5u4YSDKbYi', 'functionIndex': 1, 'functionData': '12Wfh1', 'attachment': ''}
```

#### Send
Send an NFT to another user.

```python
import py_vsys as pv

# acnt0: pv.Account
# acnt1: pv.Account
# nc: pv.NFTCtrt

resp = await nc.send(
  by=acnt0,
  recipient=acnt1.addr.data,
  tok_idx=0,
)
print(resp)
```
Example output

```
{'type': 9, 'id': '9AFRtsKvTjgGtvPhC4nGGkMkYZ8R1wDJvSL81dafzSSz', 'fee': 30000000, 'feeScale': 100, 'timestamp': 1646294591665059072, 'proofs': [{'proofType': 'Curve25519', 'publicKey': '6gmM7UxzUyRJXidy2DpXXMvrPqEF9hR1eAqsmh33J6eL', 'address': 'AU6BNRK34SLuc27evpzJbAswB6ntHV2hmjD', 'signature': '2UFsk8VGfJRTKTZjzBqsLQvymHrQuVo32CMo9sHDaGxPGKiu36teN3cboPqRTruMifX1oULPhotSgLwA1SQsVACb'}], 'contractId': 'CEu8AuKJS2Pr67RPV9dFjPAb8TL151weQsi', 'functionIndex': 2, 'functionData': '1bbXGi8m9ZYbKcwaURR5PCByaKR5gBCspa77NqkoRCLMM', 'attachment': ''}
```

#### Transfer
Transfer the ownership of an NFT to another account(e.g. user or contract).
`transfer` is the underlying action of `send`, `deposit`, and `withdraw`. It is not recommended to use transfer directly. Use `send`, `deposit`, `withdraw` instead when possible.

```python
import py_vsys as pv

# acnt0: pv.Account
# acnt1: pv.Account
# nc: pv.NFTCtrt

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
{'type': 9, 'id': 'SCzmSvR379FNicWktdBSkbLAiYpbAtHDtvVqnMiuZ19', 'fee': 30000000, 'feeScale': 100, 'timestamp': 1646295272315819008, 'proofs': [{'proofType': 'Curve25519', 'publicKey': '4Z7yUcUqa1TcHMPtp7G6XMjxTKuZWXA2hQWNz7X8XsFZ', 'address': 'AU5NsHE8eC2guo3JobD8jrGvnEDQhBP8GtW', 'signature': '37wabTeKUaNLN17KqS8rsziS4NEfVsufrpxwv3zNB8WqnT3ykrR9tcwnxSkY6kW3e3fqWm2cqFijxWwBZYnqZGaN'}], 'contractId': 'CEu8AuKJS2Pr67RPV9dFjPAb8TL151weQsi', 'functionIndex': 3, 'functionData': '1Xv7sGyd9XHiohkKw3czXTogPULzBESxCD63rpmgaR9RTCPAKj4x9Q1WtWNJ357C1atzoEW81j5BXgQfV9', 'attachment': ''}
```

#### Deposit
Deposit an NFT to a token-holding contract instance(e.g. lock contract).

Note that only the token defined in the token-holding contract instance can be deposited into it.

```python
import py_vsys as pv

# acnt0: pv.Account
# nc: pv.NFTCtrt
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
{'type': 9, 'id': '9mASDkeoJ8z9hLCoENGLRWfDSEjW7msAPExN1tGULSAs', 'fee': 30000000, 'feeScale': 100, 'timestamp': 1646295528164345088, 'proofs': [{'proofType': 'Curve25519', 'publicKey': '6gmM7UxzUyRJXidy2DpXXMvrPqEF9hR1eAqsmh33J6eL', 'address': 'AU6BNRK34SLuc27evpzJbAswB6ntHV2hmjD', 'signature': 'jWmo9BEV5WewhXZFi6cVVX918uLMG3A8YvbCaN9Xi3FE2MRBGeiGscnJ4JTMeLCGW87yLAAwcMwEFg1PBfb2jGo'}], 'contractId': 'CEu8AuKJS2Pr67RPV9dFjPAb8TL151weQsi', 'functionIndex': 4, 'functionData': '1Xv7sHDSN9pKrqwTTbWoYSpThW85PPDaJWpSGeL3sRGFVuQVfk4EcYKtk55bnWochAfaUm4nhah4YHY7F5', 'attachment': ''}
```

#### Withdraw
Withdraw an NFT from a token-holding contract instance(e.g. lock contract).

Note that only the one who deposits the token can withdraw.

```python
import py_vsys as pv

# acnt0: pv.Account
# nc: pv.NFTCtrt
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
{'type': 9, 'id': 'EF6Brq21Wi1Hv3N4z2BuVNRNfeXjb9uzv2HBVS8voRqG', 'fee': 30000000, 'feeScale': 100, 'timestamp': 1646295771726907904, 'proofs': [{'proofType': 'Curve25519', 'publicKey': '6gmM7UxzUyRJXidy2DpXXMvrPqEF9hR1eAqsmh33J6eL', 'address': 'AU6BNRK34SLuc27evpzJbAswB6ntHV2hmjD', 'signature': '4bEfdwPrwNzGkdLjP7JSvg2xdDnbPabtGK3fdGampaF9LySUHtsMJrD3V35F7C9zwgBrvMhEZfTfEB7iyY7SGquM'}], 'contractId': 'CEu8AuKJS2Pr67RPV9dFjPAb8TL151weQsi', 'functionIndex': 5, 'functionData': '1Y5SeLwhk5NvqLEeqZuAFHiVY6k713zijrRcTwsgJDd7gGwi9dxZpZCyGMqUWZJovQUcDw6MBsnz1AKygj', 'attachment': ''}
```

#### Supersede
Transfer the issuer role of the contract to a new user.
The maker of the contract has the privilege to take this action.

```python
import py_vsys as pv

# acnt0: pv.Account
# acnt1: pv.Account
# nc: pv.NFTCtrt

resp = await nc.supersede(
    by=acnt0,
    new_issuer=acnt1.addr.data,
)
print(resp)
```
Example output

```
{'type': 9, 'id': 'Cd3ksYFMxqYt6YKKm6Wfp5KPiWeGUrE6R81Dc6Egbm6s', 'fee': 30000000, 'feeScale': 100, 'timestamp': 1646295943300043008, 'proofs': [{'proofType': 'Curve25519', 'publicKey': '6gmM7UxzUyRJXidy2DpXXMvrPqEF9hR1eAqsmh33J6eL', 'address': 'AU6BNRK34SLuc27evpzJbAswB6ntHV2hmjD', 'signature': 'kDs16DYkkedVJRttCorMFSSNcLTMqTn2DkusKAvgjwb6RppGZRpwq2NbxNh2WXcfn51FhKWB8SLwiwNMdArYKXo'}], 'contractId': 'CEu8AuKJS2Pr67RPV9dFjPAb8TL151weQsi', 'functionIndex': 0, 'functionData': '1bscuEdeiiEkCJsLRbCmpioXRcWMkrs2oDToWe', 'attachment': ''}
```
