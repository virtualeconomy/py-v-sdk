"""
nft_ctrt contains NFT contract.
"""
from __future__ import annotations
from typing import Dict, Any, TYPE_CHECKING, Union

from loguru import logger

# https://stackoverflow.com/a/39757388
if TYPE_CHECKING:
    from py_vsys import account as acnt

from py_vsys import data_entry as de
from py_vsys import tx_req as tx
from py_vsys import model as md

from . import Ctrt, BaseTokCtrt


class NFTCtrt(BaseTokCtrt):
    """
    NFTCtrt is the class for VSYS NFT contract V1
    """

    CTRT_META = md.CtrtMeta.from_b58_str(
        "VJodouhmnHVDwtkBZ2NdgahT7NAgNE9EpWoZApzobhpua2nDL9D3sbHSoRRk8bEFeme2BHrXPdcq5VNJcPdGMUD54Smwatyx74cPJyet6bCWmLciHE2jGw9u5TmatjdpFSjGKegh76GvJstK3VaLagvsJJMaaKM9MNXYtgJyDr1Zw7U9PXV7N9TQnSsqz6EHMgDvd8aTDqEG7bxxAotkAgeh4KHqnk6Ga117q5AJctJcbUtD99iUgPmJrC8vzX85TEXgHRY1psW7D6daeExfVVrEPHFHrU6XfhegKv9vRbJBGL861U4Qg6HWbWxbuitgtKoBazSp7VofDtrZebq2NSpZoXCAZC8DRiaysanAqyCJZf7jJ8NfXtWej8L9vg8PVs65MrEmK8toadcyCA2UGzg6pQKrMKQEUahruBiS7zuo62eWwJBxUD1fQ1RGPk9BbMDk9FQQxXu3thSJPnKktq3aJhD9GNFpvyEAaWigp5nfjgH5doVTQk1PgoxeXRAWQNPztjNvZWv6iD85CoZqfCWdJbAXPrWvYW5FsRLW1xJ4ELRUfReMAjCGYuFWdA3CZyefpiDEWqVTe5SA6J6XeUppRyXKpKQTc6upesoAGZZ2NtFDryq22izC6D5p1i98YpC6Dk1qcKevaANKHH8TfFoQT717nrQEY2aLoWrA1ip2t5etdZjNVFmghxXEeCAGy3NcLDFHmAfcBZhHKeJHp8H8HbiMRtWe3wmwKX6mPx16ahnd3dMGCsxAZfjQcy4J1HpuCm7rHMULkixUFYRYqx85c7UpLcijLRybE1MLRjEZ5SEYtazNuiZBwq1KUcNipzrxta9Rpvt2j4WyMadxPf5r9YeAaJJp42PiC6SGfyjHjRQN4K3pohdQRbbG4HQ95NaWCy7CAwbpXRCh9NDMMQ2cmTfB3KFW2M"
    )

    class FuncIdx(Ctrt.FuncIdx):
        """
        FuncIdx is the enum class for function indexes of a contract.
        """

        SUPERSEDE = 0
        ISSUE = 1
        SEND = 2
        TRANSFER = 3
        DEPOSIT = 4
        WITHDRAW = 5

    class StateVar(Ctrt.StateVar):
        """
        StateVar is the enum class for state variables of a contract.
        """

        ISSUER = 0
        MAKER = 1

    class DBKey(Ctrt.DBKey):
        """
        DBKey is the class for DB key of a contract used to query data.
        """

        @classmethod
        def for_issuer(cls) -> NFTCtrt.DBKey:
            """
            for_issuer returns the NFTCtrt.DBKey object for querying the issuer.

            Returns:
                NFTCtrt.DBKey: The NFTCtrt.DBKey object.
            """
            b = NFTCtrt.StateVar.ISSUER.serialize()
            return cls(b)

        @classmethod
        def for_maker(cls) -> NFTCtrt.DBKey:
            """
            for_maker returns the NFTCtrt.DBKey object for querying the maker.

            Returns:
                NFTCtrt.DBKey: The NFTCtrt.DBKey object.
            """
            b = NFTCtrt.StateVar.MAKER.serialize()
            return cls(b)

    @classmethod
    async def register(
        cls,
        by: acnt.Account,
        ctrt_description: str = "",
        fee: int = md.RegCtrtFee.DEFAULT,
    ) -> NFTCtrt:
        """
        register registers an NFT Contract.

        Args:
            by (acnt.Account): The action taker.
            ctrt_description (str, optional): The description of the contract. Defaults to "".
            fee (int, optional): The fee to pay for this action. Defaults to md.RegCtrtFee.DEFAULT.

        Returns:
            NFTCtrt: The NFTCtrt object of the registered NFT contract.
        """
        data = await by._register_contract(
            tx.RegCtrtTxReq(
                data_stack=de.DataStack(),
                ctrt_meta=cls.CTRT_META,
                timestamp=md.VSYSTimestamp.now(),
                description=md.Str(ctrt_description),
                fee=md.RegCtrtFee(fee),
            )
        )
        logger.debug(data)

        return cls(
            data["contractId"],
            chain=by.chain,
        )

    @property
    async def issuer(self) -> md.Addr:
        """
        issuer queries & returns the issuer of the contract.

        Returns:
            md.Addr: The address of the issuer of the contract.
        """
        raw_val = await self._query_db_key(self.DBKey.for_issuer())
        return md.Addr(raw_val)

    @property
    async def maker(self) -> md.Addr:
        """
        maker queries & returns the maker of the contract.

        Returns:
            md.Addr: The address of the maker of the contract.
        """
        raw_val = await self._query_db_key(self.DBKey.for_maker())
        return md.Addr(raw_val)

    @property
    async def unit(self) -> int:
        """
        unit returns the unit of the NFT contract.
        This property exists to be compatible with normal token contracts.

        Returns:
            int: The unit.
        """
        return 1

    @property
    async def last_index(self) -> md.TokenIdx:
        """
        last_index returns the last index of the NFT contract.

        Returns:
            md.TokenIdx: The last index.
        """
        res = await self.chain.api.ctrt.get_last_index(self._ctrt_id.data)
        return md.TokenIdx(res["lastTokenIndex"])

    async def issue(
        self,
        by: acnt.Account,
        content: str = "",
        attachment: str = "",
        fee: int = md.ExecCtrtFee.DEFAULT,
    ) -> Dict[str, Any]:
        """
        issue issues a token of the NFT contract.

        Args:
            by (acnt.Account): The action taker.
            content (str, optional): The content of the NFT token.
            attachment (str, optional): The attachment of the action. Defaults to "".
            fee (int, optional): The fee to pay for this action. Defaults to md.ExecCtrtFee.DEFAULT.

        Returns:
            Dict[str, Any]: The response returned by the Node API
        """
        data = await by._execute_contract(
            tx.ExecCtrtFuncTxReq(
                ctrt_id=self._ctrt_id,
                func_id=self.FuncIdx.ISSUE,
                data_stack=de.DataStack(
                    de.Str.from_str(content),
                ),
                timestamp=md.VSYSTimestamp.now(),
                attachment=md.Str(attachment),
                fee=md.ExecCtrtFee(fee),
            )
        )
        logger.debug(data)
        return data

    async def send(
        self,
        by: acnt.Account,
        recipient: str,
        tok_idx: int,
        attachment: str = "",
        fee: int = md.ExecCtrtFee.DEFAULT,
    ) -> Dict[str, Any]:
        """
        send sends the NFT token from the action taker to the recipient.

        Args:
            by (acnt.Account): The action taker.
            recipient (str): The account address of the recipient.
            tok_idx (int): The index of the token within this contract to send.
            attachment (str, optional): The attachment of the action. Defaults to "".
            fee (int, optional): The fee to pay for this action. Defaults to md.ExecCtrtFee.DEFAULT.

        Returns:
            Dict[str, Any]: The response returned by the Node API
        """

        rcpt_md = md.Addr(recipient)
        rcpt_md.must_on(by.chain)

        data = await by._execute_contract(
            tx.ExecCtrtFuncTxReq(
                ctrt_id=self._ctrt_id,
                func_id=self.FuncIdx.SEND,
                data_stack=de.DataStack(
                    de.Addr(rcpt_md),
                    de.Int32(md.TokenIdx(tok_idx)),
                ),
                timestamp=md.VSYSTimestamp.now(),
                attachment=md.Str(attachment),
                fee=md.ExecCtrtFee(fee),
            )
        )
        logger.debug(data)
        return data

    async def transfer(
        self,
        by: acnt.Account,
        sender: str,
        recipient: str,
        tok_idx: int,
        attachment: str = "",
        fee: int = md.ExecCtrtFee.DEFAULT,
    ) -> Dict[str, Any]:
        """
        transfer transfers the NFT token from the sender to the recipient.

        Args:
            by (acnt.Account): The action taker.
            sender (str): The account address of the sender.
            recipient (str): The account address of the recipient.
            tok_idx (int): The index of the token within this contract to transfer.
            attachment (str, optional): The attachment of this action. Defaults to "".
            fee (int, optional): The fee to pay for this action. Defaults to md.ExecCtrtFee.DEFAULT.

        Returns:
            Dict[str, Any]: The response returned by the Node API
        """
        sender_md = md.Addr(sender)
        rcpt_md = md.Addr(recipient)

        sender_md.must_on(by.chain)
        rcpt_md.must_on(by.chain)

        data = await by._execute_contract(
            tx.ExecCtrtFuncTxReq(
                ctrt_id=self._ctrt_id,
                func_id=self.FuncIdx.TRANSFER,
                data_stack=de.DataStack(
                    de.Addr(sender_md),
                    de.Addr(rcpt_md),
                    de.Int32(md.TokenIdx(tok_idx)),
                ),
                timestamp=md.VSYSTimestamp.now(),
                attachment=md.Str(attachment),
                fee=md.ExecCtrtFee(fee),
            )
        )
        logger.debug(data)
        return data

    async def deposit(
        self,
        by: acnt.Account,
        ctrt_id: str,
        tok_idx: int,
        attachment: str = "",
        fee: int = md.ExecCtrtFee.DEFAULT,
    ) -> Dict[str, Any]:
        """
        deposit deposits the NFT token from the action taker to another contract.

        Args:
            by (acnt.Account): The action taker.
            ctrt_id (str): The id of the contract to deposit into.
            tok_idx (int): The index of the token within this contract to deposit.
            attachment (str, optional): The attachment of this action. Defaults to "".
            fee (int, optional): The fee to pay for this action. Defaults to md.ExecCtrtFee.DEFAULT.

        Returns:
            Dict[str, Any]: The response returned by the Node API
        """
        data = await by._execute_contract(
            tx.ExecCtrtFuncTxReq(
                ctrt_id=self._ctrt_id,
                func_id=self.FuncIdx.DEPOSIT,
                data_stack=de.DataStack(
                    de.Addr(md.Addr(by.addr.data)),
                    de.CtrtAcnt(md.CtrtID(ctrt_id)),
                    de.Int32(md.TokenIdx(tok_idx)),
                ),
                timestamp=md.VSYSTimestamp.now(),
                attachment=md.Str(attachment),
                fee=md.ExecCtrtFee(fee),
            )
        )
        logger.debug(data)
        return data

    async def withdraw(
        self,
        by: acnt.Account,
        ctrt_id: str,
        tok_idx: int,
        attachment: str = "",
        fee: int = md.ExecCtrtFee.DEFAULT,
    ) -> Dict[str, Any]:
        """
        withdraw withdraws the token from another contract to the action taker.

        Args:
            by (acnt.Account): The action taker.
            ctrt_id (str): The id of the contract to withdraw from.
            tok_idx (int): The index of the token within this contract to withdraw.
            attachment (str, optional): The attachment of this action. Defaults to "".
            fee (int, optional): The fee to pay for this action. Defaults to md.ExecCtrtFee.DEFAULT.

        Returns:
            Dict[str, Any]: The response returned by the Node API
        """
        data = await by._execute_contract(
            tx.ExecCtrtFuncTxReq(
                ctrt_id=self._ctrt_id,
                func_id=self.FuncIdx.WITHDRAW,
                data_stack=de.DataStack(
                    de.CtrtAcnt(md.CtrtID(ctrt_id)),
                    de.Addr(md.Addr(by.addr.data)),
                    de.Int32(md.TokenIdx(tok_idx)),
                ),
                timestamp=md.VSYSTimestamp.now(),
                attachment=md.Str(attachment),
                fee=md.ExecCtrtFee(fee),
            )
        )
        logger.debug(data)
        return data

    async def supersede(
        self,
        by: acnt.Account,
        new_issuer: str,
        attachment: str = "",
        fee: int = md.ExecCtrtFee.DEFAULT,
    ) -> Dict[str, Any]:
        """
        supersede transfers the issuer role of the contract to a new account.

        Args:
            by (acnt.Account): The action taker.
            new_issuer (str): The account address of the new issuer.
            attachment (str, optional): The attachment of this action. Defaults to "".
            fee (int, optional): The fee to pay for this action. Defaults to md.ExecCtrtFee.DEFAULT.

        Returns:
            Dict[str, Any]: The response returned by the Node API
        """

        new_issuer_md = md.Addr(new_issuer)
        new_issuer_md.must_on(by.chain)

        data = await by._execute_contract(
            tx.ExecCtrtFuncTxReq(
                ctrt_id=self._ctrt_id,
                func_id=self.FuncIdx.SUPERSEDE,
                data_stack=de.DataStack(
                    de.Addr(new_issuer_md),
                ),
                timestamp=md.VSYSTimestamp.now(),
                attachment=md.Str(attachment),
                fee=md.ExecCtrtFee(fee),
            )
        )
        logger.debug(data)
        return data


class NFTCtrtV2Base(NFTCtrt):
    """
    NFTCtrtV2Base is the base class for VSYS NFT contract V2
    """

    class FuncIdx(Ctrt.FuncIdx):
        """
        FuncIdx is the enum class for function indexes of a contract.
        """

        SUPERSEDE = 0
        ISSUE = 1
        UPDATE_LIST = 2
        SEND = 3
        TRANSFER = 4
        DEPOSIT = 5
        WITHDRAW = 6

    class StateVar(Ctrt.StateVar):
        """
        StateVar is the enum class for state variables of a contract.
        """

        ISSUER = 0
        MAKER = 1
        REGULATOR = 2

    class StateMapIdx(Ctrt.StateMapIdx):
        """
        StateMapIdx is the enum class for state map indexes.
        """

        IS_IN_LIST = 0

    class DBKey(NFTCtrt.DBKey):
        """
        DBKey is the class for DB key of a contract used to query data.
        """

        @classmethod
        def for_regulator(cls) -> NFTCtrtV2Base.DBKey:
            """
            for_regulator returns the DBKey for querying the regulator.

            Returns:
                NFTCtrtV2Base.DBKey: The DBKey.
            """
            b = NFTCtrtV2Base.StateVar.REGULATOR.serialize()
            return cls(b)

        @classmethod
        def _for_is_in_list(
            cls, addr_data_entry: Union[de.Addr, de.CtrtAcnt]
        ) -> NFTCtrtV2Base.DBKey:
            """
            _for_is_in_list returns the DBKey for querying the status of if the address in the given data entry
            is in the list.
            It's a helper method for is_XXX_in_list

            Args:
                addr_data_entry (Union[de.Addr, de.CtrtAcnt]): The data entry for the address.

            Returns:
                NFTCtrtV2Base.DBKey: The DBKey.
            """
            stmp = NFTCtrtV2Base.StateMap(
                idx=NFTCtrtV2Base.StateMapIdx.IS_IN_LIST,
                data_entry=addr_data_entry,
            )
            b = stmp.serialize()
            return cls(b)

        @classmethod
        def for_is_user_in_list(cls, addr: str) -> NFTCtrtV2Base.DBKey:
            """
            for_is_user_in_list returns the DBKey for querying the status of if
            the given user address is in the list.

            Args:
                addr (str): The user address.

            Returns:
                NFTCtrtV2Base.DBKey: The DBKey.
            """
            addr_de = de.Addr(md.Addr(addr))
            return cls._for_is_in_list(addr_de)

        @classmethod
        def for_is_ctrt_in_list(cls, addr: str) -> NFTCtrtV2Base.DBKey:
            """
            for_is_ctrt_in_list returns the DBKey for querying the status of if
            the given contract address is in the list.

            Args:
                addr (str): The contract address.

            Returns:
                NFTCtrtV2Base.DBKey: The DBKey.
            """
            addr_de = de.CtrtAcnt(md.CtrtID(addr))
            return cls._for_is_in_list(addr_de)

    @property
    async def regulator(self) -> md.Addr:
        """
        regulator queries & returns the regulator of the contract.

        Returns:
            md.Addr: The address of the regulator of the contract.
        """
        raw_val = await self._query_db_key(self.DBKey.for_regulator())
        return md.Addr(raw_val)

    async def _is_in_list(self, db_key: NFTCtrtV2Base.DBKey) -> bool:
        """
        _is_in_list queries & returns the status of whether the address is
        in the list for the given db_key.

        Args:
            db_key (NFTCtrtV2Base.DBKey): The DBKey for the query.

        Returns:
            bool: If the address is in the list.
        """
        data = await self._query_db_key(db_key)
        return data == "true"

    async def is_user_in_list(self, addr: str) -> bool:
        """
        is_user_in_list queries & returns the status of whether the user address in the white/black list.

        Args:
            addr (str): The address to check.

        Returns:
            bool: If the address is in the list.
        """
        return await self._is_in_list(self.DBKey.for_is_user_in_list(addr))

    async def is_ctrt_in_list(self, addr: str) -> bool:
        """
        is_ctrt_in_list queries & returns the status of whether the contract address in the white/black list.

        Args:
            addr (str): The address to check.

        Returns:
            bool: If the address is in the list.
        """
        return await self._is_in_list(self.DBKey.for_is_ctrt_in_list(addr))

    async def _update_list(
        self,
        by: acnt.Account,
        addr_data_entry: Union[de.Addr, de.CtrtAcnt],
        val: bool,
        attachment: str = "",
        fee: int = md.ExecCtrtFee.DEFAULT,
    ) -> Dict[str, Any]:
        """
        _update_list updates the presence of the address within the given data entry in the list.
        It's the helper method for update_list.

        Args:
            by (acnt.Account): The action taker.
            addr_data_entry (Union[de.Addr, de.CtrtAcnt]): The data entry for the address to update.
            val (bool): The value to update to.
            attachment (str, optional): The attachment of this action. Defaults to "".
            fee (int, optional): The fee to pay for this action. Defaults to md.ExecCtrtFee.DEFAULT.

        Returns:
            Dict[str, Any]: The response returned by the Node API
        """

        data = await by._execute_contract(
            tx.ExecCtrtFuncTxReq(
                ctrt_id=self._ctrt_id,
                func_id=self.FuncIdx.UPDATE_LIST,
                data_stack=de.DataStack(
                    addr_data_entry,
                    de.Bool(md.Bool(val)),
                ),
                timestamp=md.VSYSTimestamp.now(),
                attachment=md.Str(attachment),
                fee=md.ExecCtrtFee(fee),
            )
        )
        logger.debug(data)
        return data

    async def update_list_user(
        self,
        by: acnt.Account,
        addr: str,
        val: bool,
        attachment: str = "",
        fee: int = md.ExecCtrtFee.DEFAULT,
    ) -> Dict[str, Any]:
        """
        update_list_user updates the presence of the user address in the list.

        Args:
            by (acnt.Account): The action taker.
            addr (str): The account address of the user.
            val (bool): The value to update to.
            attachment (str, optional): The attachment of this action. Defaults to "".
            fee (int, optional): The fee to pay for this action. Defaults to md.ExecCtrtFee.DEFAULT.

        Returns:
            Dict[str, Any]: The response returned by the Node API
        """
        user_md = md.Addr(addr)
        user_md.must_on(by.chain)
        return await self._update_list(by, de.Addr(user_md), val, attachment, fee)

    async def update_list_ctrt(
        self,
        by: acnt.Account,
        addr: str,
        val: bool,
        attachment: str = "",
        fee: int = md.ExecCtrtFee.DEFAULT,
    ) -> Dict[str, Any]:
        """
        update_list_user updates the presence of the contract address in the list.

        Args:
            by (acnt.Account): The action taker.
            addr (str): The account address of the contract.
            val (bool): The value to update to.
            attachment (str, optional): The attachment of this action. Defaults to "".
            fee (int, optional): The fee to pay for this action. Defaults to md.ExecCtrtFee.DEFAULT.

        Returns:
            Dict[str, Any]: The response returned by the Node API
        """
        ctrt_md = md.CtrtID(addr)
        return await self._update_list(by, de.CtrtAcnt(ctrt_md), val, attachment, fee)

    async def supersede(
        self,
        by: acnt.Account,
        new_issuer: str,
        new_regulator: str,
        attachment: str = "",
        fee: int = md.ExecCtrtFee.DEFAULT,
    ) -> Dict[str, Any]:
        """
        supersede transfers the issuer role of the contract to a new account.

        Args:
            by (acnt.Account): The action taker.
            new_issuer (str): The account address of the new issuer.
            new_regulator (str): The account address of the new regulator.
            attachment (str, optional): The attachment of this action. Defaults to "".
            fee (int, optional): The fee to pay for this action. Defaults to md.ExecCtrtFee.DEFAULT.

        Returns:
            Dict[str, Any]: The response returned by the Node API
        """

        new_issuer_md = md.Addr(new_issuer)
        new_issuer_md.must_on(by.chain)

        new_regulator_md = md.Addr(new_regulator)
        new_regulator_md.must_on(by.chain)

        data = await by._execute_contract(
            tx.ExecCtrtFuncTxReq(
                ctrt_id=self._ctrt_id,
                func_id=self.FuncIdx.SUPERSEDE,
                data_stack=de.DataStack(
                    de.Addr(new_issuer_md),
                    de.Addr(new_regulator_md),
                ),
                timestamp=md.VSYSTimestamp.now(),
                attachment=md.Str(attachment),
                fee=md.ExecCtrtFee(fee),
            )
        )
        logger.debug(data)
        return data


class NFTCtrtV2Whitelist(NFTCtrtV2Base):
    """
    NFTCtrtV2Whitelist is the class for VSYS NFT contract V2 with whitelist
    """

    CTRT_META = md.CtrtMeta.from_b58_str(
        "3g9JzsVg6kPLJKHuWAbMKgiH2aeZt5VTTdrVNeVBQuviDGJnyLrPB4FHtt6Np2rKXy2ZCZftZ1SkNRifVAasWGF5dYt1zagnDrgE52Forq9QyXq2vmyq8NUMVuLfHFDgUC7d7tJPSVZdmhDNzc3cR9WcobXqcR3x923wmTZp63ztxgzdk4cV39TJLoTBLFguFKjqetkU7WUmP6ivMfcvDzMBzgq48fjJ1AYn5fxt31ZV6tAorCQ4w2zfekL8aUEhePgR66RXSBggiqQhTcw7dGg8xkGtRh3wkAVEbFuZa78R1C9cUUytbYM5fi17AE5q9UEgegxMMpZgsk9YNHs4mx4NPLj6Rz5DK3QwbeUbaVWceSqssYS6GodJ41bEm84x3aQrqQK33tHSPRy9uAr9ku773fZuHWPEeNoEDdsnUVsxCKQ7AyM5K1JVFRFwMABGGAnkYsFV23pfLFktBSvAJkzo8Hi6Wss7ZEBgSDeCJJohqoxmsR7L8kcfjRwy3Rb7VU76LMuqGrBfb39uUy5qdxRqAMFtwE4imkxxX6akuR7RMd3RmKQ2W7TXMuWZNyJHd4c17ZJrSCQNAXQ2iKXxSbUoDUmetuCud81SQonTjomq9RsGqRvaV2iGjHUb4wvUuKhodE4dF8xrNWXQxfPpwed1mUEuUPmhppY7Lg7p5EJyXVYDr4ybdsmYohDFgTDbGs3mZBmgUpEVAUC4vJrXqWWv8gjw8j5xabF6QfbtcWrbrVu4sTtMGzybVAoeB4b1x3Rkd67ABWnmzHfDxMopfb21TSDGpWLnSQeRn2gA2jnLUokb8FXUHG5qttmLNzG7RY1XRmC7TKRQ3X5JqGbHbN4rhUxU8iQUKpACWsyGuEP8VrUNvx41sMEbfReZ8ay7v2cQEtmw5uFfXMmAcsQBrRdxsHTaN5Cpu7Ak1pRvZzQKKesWuHLuUgNStdqVpHih4cTk1YzoJJ34spDa7FYhzTWTSVJBwHvYy5WQxrXnXAXBmMeNVroX8x9gT38LeqJ2z4KoAWnj2o1waKB8TC1JXet7sXHttGWDs7YHJHNEy5CcWkVCPnt5xVTq9ZwPkc4EhLQDWortL35e75vyQR3F3tW2Pr89UiPSNWEXxC5L8apavKVyv9zUcWUwShd5bdcfKa1CnLSMhW9DE6CT4APWKuPdxW9hLgkYZziJtN4WebcbA5PbG8hrkhU2E7easz3pRJQ49vhMtSf7tKTf9NDwZuuZ9ix9q5TZMzYvNbg5rk9P6uoPLRZk61J2LpQv8K7YLBrcWSduPsxWWjiCvxL7bW8vA8gWQocxfuXiM5i3wdA1zLx8As3Ydufi2S3nk23BwRjZhjhh7BEq7p1nwpqP97PqqW2CpMJspEHdHCzRR3fBJw6mLdSGAYeia22r2uJm1o73WrPFTt9vQwCLXMKS3WMd3GpRmR36n3C9Ed7xdnFcRDYZBgLis63UEvczGvH9HS8MMHkoAXE3wuahEzYZEd1NxJXSXFhe2h6DJbABXQKMMkZdPQmGJkDhBPTh9nZ9DgGHhnnitxQ5ESfxqvqxwuVubAXTt3psg8LS2B16mjDGh9"
    )


class NFTCtrtV2Blacklist(NFTCtrtV2Base):
    """
    NFTCtrtV2Blacklist is the class for VSYS NFT contract V2 with blacklist
    """

    CTRT_META = md.CtrtMeta.from_b58_str(
        "3g9JzsVg6kPLJKHuWAbMKgiH2aeZt5VTTdrVNeVBQuviDGJnyLrPB4FHtt6Np2rKXy2ZCZftZ1SkNRifVAasWGF5dYt1zagnDrgE52Forq9QyXq2vmyq8NUMVuLfHFDgUC7d7tJPSVZdmhDNzc3cR9WcobXqcR3x923wmTZp63ztxgzdk4cV39TJLoTBLFguFKjqetkU7WUmP6ivMfcvDzMBzgq48fjJ1AYn5fxt31ZV6tAorCQ4w2zfekL8aUEhePgR66RXSBggiqQhTcw7dGg8xkGtRh3wkAVEbFuZa78R1Bw8Fc7fND3crHRj8pY66QYiaksdHixYVm4R68ez9K1ndEZq1ShQBs5DbvyoFGc4Dr1Yosv5VKJbqaB5fu7ZZ8SvB5RVYqSsN9tTTmUinNmJ4v63DWvH2N7WnFq8JYPL4RpEpnvBYnSUdAxN44skS45uVi5F4bkueAXbgUeoir82hTgLvgnf573Ziw9Mon4STtfhP8Y5DKTqA2gM44MmVkNWW7WwNDXerdYwD65QMG7BSSU9UhH6eNvay2LYXNph9heAWYwKcQPJnA7niSZto23XaFoU8kGRUoDNvofQw1XJkdTgVgLt5yz8HbGxnXT5AdKa3YNyAnq4KgXjU4W3Xj8xWqpYHX54C8GQF7poCM4E5XNDXbgExoK3bS4WHkbmwJJJzJ6MtsiyZnmSYGs7HhfcueFH4SjjNKevcntrC4Kenc6tygSWrSzefdSC78XrQ5bgSp24wKoX4WxUUUky8KB9NvWGHYF3x8Bg59HwH67haNB9wejM8Jj5a88XoVTYAqMh6z8zuZUqANshYRaxjxYLaV2VATrTKM13zMARaBVoDRFKtYiE8CmFKeequ9HdWix6CmCEtKQdCC4UmtYJ1Ch4qpfjKyMP4Bd7YbKLg928ZHFiLN2Uq1KLfbn1V83Xe1xPGwkX1TCsJpBXyqmsByaYUckFgkCNNvkpuAs1dA8HLLrnd1Tx6zT99vDaPUr2k9nLQ6o1hjPyK1EPBVg5zxrnaSP446m54CemwNPa1UECFx6sEhrL1EbL1yQR7cfMnrr82z9iSiSMZMubfEhPyuD58TYjSRGd1XRSnhjo1tBwN2k27RsNtdhAmH2u57eCfDQpnMUnBkSZj71o2Kk5cMfMxNWLBYr1w7Ma8yJriQYNedNo5fG5XVubmmd5H7YpVAjPKWVVru3SQXR7AHcLv834pCQD7EjYEbNdFeheaDiA1yp7amZrig3cd6jabMPoDSvP1GxX8HrUnv4hCvSmDivGpFvcGJnGbNuSHTP8qHTAf8jVFeMpeMiLH9rP9qcpMAhh9mAzmj5pVhZZBuiWFor8empJoKGv2RcUFRALEFDXoYaPrri7oCypNeWS4eiVum8fm5hx3CMY9N2HMqMrokCCTHceiHYKfgjYRnXaJsJUs28rPyqqxAaxUj3qNpaB2D6x6nc4fKLSZyuUCgZSmRPPBWWugRNRDxppG6ecA1hkNZDX2NQY9erhuMYX9jhVCLb6NLVe5euWFkvBjF4Y7qfpKM1uLSZvxd4gmA5VGA99vKFkYUwvBB5TNPnupdECD9"
    )
