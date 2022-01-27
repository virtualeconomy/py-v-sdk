"""
account contains account-related resources
"""
from __future__ import annotations
import os
from typing import Any, Dict, TYPE_CHECKING, Type, Union

from loguru import logger

# https://stackoverflow.com/a/39757388
if TYPE_CHECKING:
    from py_v_sdk import chain as ch
    from py_v_sdk import api

from py_v_sdk import model as md
from py_v_sdk import tx_req as tx
from py_v_sdk import dbput as dp
from py_v_sdk.utils.crypto import hashes as hs
from py_v_sdk.utils.crypto import curve_25519 as curve
from py_v_sdk import words as wd


class Wallet:
    """
    Wallet is a collection of accounts.
    """

    def __init__(self, seed: md.Seed) -> None:
        """
        Args:
            seed (md.Seed): The seed of the wallet.
        """
        self._seed = seed

    @property
    def seed(self) -> md.Seed:
        """
        seed returns the seed of the wallet.

        Returns:
            md.Seed: The seed of the wallet.
        """
        return self._seed

    @classmethod
    def from_seed_str(cls, s: str) -> Wallet:
        """
        from_seed_str creates a wallet from a seed string.

        Args:
            s (str): The seed string.

        Returns:
            Wallet: The wallet.
        """
        return cls(md.Seed(s))

    @classmethod
    def register(cls) -> Wallet:
        """
        register creates a new wallet with a newly generated seed.

        Returns:
            Wallet: The wallet.
        """
        return cls(cls.new_seed())

    def get_account(self, chain: ch.Chain, nonce: int = 0) -> Account:
        """
        get_account gets the account of the nonce of the wallet on the given chain.

        Args:
            chain (ch.Chain): The chain that the account is on.
            nonce (int, optional): The nonce of the account. Defaults to 0.

        Returns:
            Account: The account.
        """
        return Account(
            chain=chain,
            wallet=self,
            nonce=nonce,
        )

    @staticmethod
    def new_seed() -> md.Seed:
        """
        new_seed generates a seed for a wallet

        Returns:
            md.Seed: The generated seed.
        """
        word_cnt = 2048
        words = []

        for _ in range(5):
            r = os.urandom(4)
            x = r[3] + (r[2] << 8) + (r[1] << 16) + (r[0] << 24)

            w1 = x % word_cnt
            w2 = (x // word_cnt + w1) % word_cnt
            w3 = (x // word_cnt // word_cnt + w2) % word_cnt

            words.append(wd.WORDS[w1])
            words.append(wd.WORDS[w2])
            words.append(wd.WORDS[w3])

        s = " ".join(words)
        return md.Seed(s)

    @staticmethod
    def get_key_pair(acnt_seed_hash: bytes) -> md.KeyPair:
        """
        get_key_pair generates a key pair based on the given account seed hash.

        Args:
            acnt_seed_hash (bytes): The account seed hash.

        Returns:
            md.KeyPair: The generated key pair.
        """
        pri_key = curve.gen_pri_key(acnt_seed_hash)
        pub_key = curve.gen_pub_key(pri_key)

        return md.KeyPair(
            pub=md.PubKey.from_bytes(pub_key),
            pri=md.PriKey.from_bytes(pri_key),
        )

    @staticmethod
    def get_addr(pub_key: bytes, addr_ver: int, chain_id: ch.ChainID) -> md.Bytes:
        """
        get_addr generates the address based on the given data.

        Args:
            pub_key (bytes): The public key.
            addr_ver (int): The address version.
            chain_id (ch.ChainID): The chain ID.

        Returns:
            md.Bytes: The generated address.
        """

        def ke_bla_hash(b: bytes) -> bytes:
            return hs.keccak256_hash(hs.blake2b_hash(b))

        raw_addr: str = (
            chr(addr_ver) + chain_id.value + ke_bla_hash(pub_key).decode("latin-1")[:20]
        )

        checksum: str = ke_bla_hash(raw_addr.encode("latin-1")).decode("latin-1")[:4]

        b = bytes((raw_addr + checksum).encode("latin-1"))
        return md.Bytes(b)

    @staticmethod
    def get_acnt_seed_hash(seed: str, nonce: int) -> md.Bytes:
        """
        get_acnt_seed_hash generates account seed hash based on the given seed & nonce.

        Args:
            seed (str): The account seed.
            nonce (int): The account nonce.

        Returns:
            md.Bytes: The generated account seed hash.
        """
        b = hs.sha256_hash(
            hs.keccak256_hash(hs.blake2b_hash(f"{nonce}{seed}".encode("latin-1")))
        )
        return md.Bytes(b)


class Account:
    """
    Account is a class for an account on the chain.
    """

    ADDR_VER = 5

    def __init__(self, chain: ch.Chain, wallet: Wallet, nonce: int = 0) -> Account:
        """
        Args:
            chain (ch.Chain): The chain that the account is on.
            wallet (Wallet): The wallet that owns the account.
            nonce (int, optional): The nonce of the account. Defaults to 0.
        """
        self._chain = chain
        self._wallet = wallet
        self._nonce = md.Nonce(nonce)

        self._acnt_seed_hash = wallet.get_acnt_seed_hash(wallet.seed.data, nonce)
        self._key_pair = wallet.get_key_pair(self._acnt_seed_hash.data)
        self._addr = wallet.get_addr(
            self.key_pair.pub.bytes, self.ADDR_VER, self.chain.chain_id
        )

    @property
    def chain(self) -> ch.Chain:
        """
        chain returns the chain that the account is on.

        Returns:
            ch.Chain: The chain that the account is on.
        """
        return self._chain

    @property
    def api(self) -> api.NodeAPI:
        """
        api returns the NodeAPI object that the account's chain uses.

        Returns:
            api.NodeAPI: The NodeAPI object that the account's chain uses.
        """
        return self._chain.api

    @property
    def wallet(self) -> Wallet:
        """
        wallet returns the Wallet object for the wallet the account belongs to.

        Returns:
            Wallet: The wallet object.
        """
        return self._wallet

    @property
    def nonce(self) -> md.Nonce:
        """
        nonce returns the account's nonce.

        Returns:
            int: The account's nonce.
        """
        return self._nonce

    @property
    def acnt_seed_hash(self) -> md.Bytes:
        """
        acnt_seed_hash returns the account's account seed hash.

        Returns:
            md.Bytes: The account's account seed hash.
        """
        return self._acnt_seed_hash

    @property
    def key_pair(self) -> md.KeyPair:
        """
        key_pair returns the account's key pair.

        Returns:
            md.KeyPair: The account's key pair.
        """
        return self._key_pair

    @property
    def addr(self) -> md.Bytes:
        """
        addr returns the account's address.

        Returns:
            md.Bytes: The account's address.
        """
        return self._addr

    @property
    async def balance(self) -> int:
        """
        balance returns the account's balance.

        Returns:
            int: The account's balance.
        """
        resp = await self.api.addr.get_balance(self.addr.b58_str)
        return resp["balance"]

    @property
    async def effective_balance(self) -> int:
        """
        effective_balance returns the account's effective balance(i.e. The balance that can be spent).

        Returns:
            int: The account's effective balance.
        """
        resp = await self.api.addr.get_effective_balance(self.addr.b58_str)
        return resp["balance"]

    async def _pay(self, req: tx.PaymentTxReq) -> Dict[str, Any]:
        """
        _pay sends a payment transaction request on behalf of the account.

        Args:
            req (tx.PaymentTxReq): The payment transaction request.

        Returns:
            Dict[str, Any]: The response returned by the Node API.
        """
        return await self.api.vsys.broadcast_payment(
            req.to_broadcast_payment_payload(self.key_pair)
        )

    async def pay(
        self,
        recipient: str,
        amount: Union[int, float],
        attachment: str = "",
        fee: int = md.PaymentFee.DEFAULT,
    ) -> Dict[str, Any]:
        """
        pay pays the VSYS coins from the action taker to the recipient.

        Args:
            recipient (str): The account address of the recipient.
            amount (Union[int, float]): The amount of VSYS coins to send.
            attachment (str, optional): The attachment of the action. Defaults to "".
            fee (int, optional): The fee to pay for this action. Defaults to md.PaymentFee.DEFAULT.

        Returns:
            Dict[str, Any]: The response returned by the Node API.
        """
        rcpt_md = md.Addr(recipient)
        rcpt_md.must_on(self.chain)

        data = await self._pay(
            tx.PaymentTxReq(
                recipient=rcpt_md,
                amount=md.VSYS.for_amount(amount),
                timestamp=md.VSYSTimestamp.now(),
                attachment=md.Str(attachment),
                fee=md.PaymentFee(fee),
            )
        )
        logger.debug(data)
        return data

    async def _lease(self, req: tx.LeaseTxReq) -> Dict[str, Any]:
        """
        _lease sends a leasing transaction request on behalf of the account.

        Args:
            req (tx.LeaseTxReq): The leasing transaction request.

        Returns:
            Dict[str, Any]: The response returned by the Node API.
        """
        return await self.api.leasing.broadcast_lease(
            req.to_broadcast_leasing_payload(self.key_pair)
        )

    async def lease(
        self,
        supernode_addr: str,
        amount: Union[int, float],
        fee: int = md.LeasingFee.DEFAULT,
    ) -> Dict[str, Any]:
        """
        lease leases the VSYS coins from the action taker to the recipient(a supernode).

        Args:
            supernode_addr (str): The account address of the supernode to lease to.
            amount (Union[int, float]): The amount of VSYS coins to send.
            fee (int, optional): The fee to pay for this action. Defaults to md.LeasingFee.DEFAULT.

        Returns:
            Dict[str, Any]: The response returned by the Node API.
        """
        addr_md = md.Addr(supernode_addr)
        addr_md.must_on(self.chain)

        data = await self._lease(
            tx.LeaseTxReq(
                supernode_addr=addr_md,
                amount=md.VSYS.for_amount(amount),
                timestamp=md.VSYSTimestamp.now(),
                fee=md.LeasingFee(fee),
            )
        )
        logger.debug(data)
        return data

    async def _cancel_lease(self, req: tx.LeaseCancelTxReq) -> Dict[str, Any]:
        """
        _cancel_lease sends a leasing cancel transaction request on behalf of the account.

        Args:
            req (tx.LeaseCancelTxReq): The leasing cancel transaction request.

        Returns:
            Dict[str, Any]: The response returned by the Node API.
        """
        return await self.api.leasing.broadcast_cancel(
            req.to_broadcast_cancel_payload(self.key_pair)
        )

    async def cancel_lease(
        self,
        leasing_tx_id: str,
        fee: int = md.LeasingCancelFee.DEFAULT,
    ) -> Dict[str, Any]:
        """
        cancel_lease cancels the leasing.

        Args:
            leasing_tx_id (str): The transaction ID of the leasing.
            fee (int, optional): The fee to pay for this action. Defaults to md.LeasingCancelFee.DEFAULT.

        Returns:
            Dict[str, Any]: The response returned by the Node API.
        """

        data = await self._cancel_lease(
            tx.LeaseCancelTxReq(
                leasing_tx_id=md.TXID(leasing_tx_id),
                timestamp=md.VSYSTimestamp.now(),
                fee=md.LeasingCancelFee(fee),
            )
        )
        logger.debug(data)
        return data

    async def _register_contract(self, req: tx.RegCtrtTxReq) -> Dict[str, Any]:
        """
        _register_contract sends a register contract transaction on behalf of the account.

        Args:
            req (tx.RegCtrtTxReq): The register contract transaction request.

        Returns:
            Dict[str, Any]: The response returned by the Node API.
        """
        return await self.api.ctrt.broadcast_register(
            req.to_broadcast_register_payload(self.key_pair)
        )

    async def _execute_contract(self, req: tx.ExecCtrtFuncTxReq) -> Dict[str, Any]:
        """
        _execute_contract sends an execute contract transaction on behalf of the account.

        Args:
            req (tx.ExecCtrtFuncTxReq): The execute contract transaction request.

        Returns:
            Dict[str, Any]: The response returned by the Node API.
        """
        return await self.api.ctrt.broadcast_execute(
            req.to_broadcast_execute_payload(self.key_pair)
        )

    async def _db_put(self, req: tx.DBPutTxReq) -> Dict[str, Any]:
        """
        _db_put sends a DB Put transaction on behalf of the account.

        Args:
            req (tx.DBPutTxReq): The DB Put transaction request.

        Returns:
            Dict[str, Any]: The response returned by the Node API.
        """
        return await self.api.db.broadcasts_put(
            req.to_broadcast_put_payload(self.key_pair)
        )

    async def db_put(
        self,
        db_key: str,
        data: str,
        data_type: Type[dp.DBPutData] = dp.ByteArray,
        fee: int = md.DBPutFee.DEFAULT,
    ) -> Dict[str, Any]:
        """
        db_put stores the data under the key onto the chain.

        Args:
            db_key (str): The db key of the data.
            data (str): The data to put.
            data_type (Type[dp.DBPutData], optional): The type of the data(i.e. how should the string be parsed).
                Defaults to dp.ByteArray.
            fee (int, optional): The fee to pay for this action. Defaults to md.DBPutFee.DEFAULT.

        Returns:
            Dict[str, Any]: The response returned by the Node API.
        """
        data = await self._db_put(
            tx.DBPutTxReq(
                db_key=dp.DBPutKey.from_str(db_key),
                data=dp.DBPutData.new(data, data_type),
                timestamp=md.VSYSTimestamp.now(),
                fee=md.DBPutFee(fee),
            )
        )
        logger.debug(data)
        return data
