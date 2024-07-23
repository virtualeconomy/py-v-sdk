import asyncio
import time
import base58

import pytest

import py_vsys as pv
from py_vsys.utils.crypto import hashes as hs
from py_vsys import data_entry as de
from test.func_test import conftest as cft


class TestAtomicSwapCtrt:
    """
    TestAtomicSwapCtrt is the collection of functional tests of atomic swap contract.
    """

    @pytest.fixture
    async def new_maker_tok_ctrt(self, acnt0: pv.Account) -> pv.TokCtrtWithoutSplit:
        """
        new_maker_tok_ctrt is the fixture that registers a new token contract of maker's.

        Args:
            acnt0 (pv.Account): the account of nonce 0.

        Returns:
            pv.TokCtrtWithoutSplit: the TokCtrtWithoutSplit instance.
        """
        tc = await pv.TokCtrtWithoutSplit.register(acnt0, 100, 1)
        await cft.wait_for_block()
        return tc

    @pytest.fixture
    async def new_taker_tok_ctrt(self, acnt1: pv.Account) -> pv.TokCtrtWithoutSplit:
        """
        new_taker_tok_ctrt is the fixture that registers a new token contract of taker's.

        Args:
            acnt1 (pv.Account): the account of nonce 0.

        Returns:
            pv.TokCtrtWithoutSplit: the TokCtrtWithoutSplit instance.
        """
        tc = await pv.TokCtrtWithoutSplit.register(acnt1, 100, 1)
        await cft.wait_for_block()
        return tc

    @pytest.fixture
    async def new_maker_tok_ctrt_with_tok(
        self, new_maker_tok_ctrt: pv.TokCtrtWithoutSplit, acnt0: pv.Account
    ) -> pv.TokCtrtWithoutSplit:
        """
        new_maker_tok_ctrt_with_tok is the fixture that registers a new TokenWithoutSplit contract and issues tokens right after it.

        Args:
            new_maker_tok_ctrt (pv.TokCtrtWithoutSplit): The fixture that registers a new TokenWithoutSplit contract.
            acnt0 (pv.Account): The account of nonce 0.

        Returns:
            pv.TokCtrtWithoutSplit: The TokCtrtWithoutSplit instance.
        """
        tc = new_maker_tok_ctrt
        await tc.issue(acnt0, 100)
        await cft.wait_for_block()
        return tc

    @pytest.fixture
    async def new_taker_tok_ctrt_with_tok(
        self, new_taker_tok_ctrt: pv.TokCtrtWithoutSplit, acnt1: pv.Account
    ) -> pv.TokCtrtWithoutSplit:
        """
        new_taker_tok_ctrt_with_tok is the fixture that registers a new TokenWithoutSplit contract and issues tokens right after it.

        Args:
            new_taker_tok_ctrt (pv.TokCtrtWithoutSplit): The fixture that registers a new TokenWithoutSplit contract.
            acnt1 (pv.Account): The account of nonce 1.

        Returns:
            pv.TokCtrtWithoutSplit: The TokCtrtWithoutSplit instance.
        """
        tc = new_taker_tok_ctrt
        await tc.issue(acnt1, 100)
        await cft.wait_for_block()
        return tc

    @pytest.fixture
    async def new_maker_atomic_swap_ctrt(
        self,
        new_maker_tok_ctrt_with_tok: pv.TokCtrtWithoutSplit,
        acnt0: pv.Account,
    ) -> pv.AtomicSwapCtrt:
        """
        new_maker_atomic_swap_ctrt is the fixture that registers a new atomic swap contract.

        Args:
            new_maker_tok_ctrt_with_tok (pv.TokCtrtWithoutSplit): The fixture that registers a new atomic swap contract and issues tokens right after it.
            acnt0 (pv.Account): The account of nonce 0.

        Returns:
            pv.AtomicSwapCtrt: The AtomicSwapCtrt instance.
        """
        tc = new_maker_tok_ctrt_with_tok

        ac = await pv.AtomicSwapCtrt.register(acnt0, tc.tok_id.data)
        await cft.wait_for_block()

        await tc.deposit(acnt0, ac.ctrt_id.data, 100)
        await cft.wait_for_block()

        return ac

    @pytest.fixture
    async def new_taker_atomic_swap_ctrt(
        self,
        new_taker_tok_ctrt_with_tok: pv.TokCtrtWithoutSplit,
        acnt1: pv.Account,
    ) -> pv.AtomicSwapCtrt:
        """
        new_taker_atomic_swap_ctrt is the fixture that registers a new atomic swap contract.

        Args:
            new_taker_tok_ctrt_with_tok (pv.TokCtrtWithoutSplit): The fixture that registers a new token contract and issues tokens right after it.
            acnt1 (pv.Account): The account of nonce 1.

        Returns:
            pv.AtomicSwapCtrt: The AtomicSwapCtrt instance.
        """
        tc = new_taker_tok_ctrt_with_tok

        ac = await pv.AtomicSwapCtrt.register(acnt1, tc.tok_id.data)
        await cft.wait_for_block()

        await tc.deposit(acnt1, ac.ctrt_id.data, 100)
        await cft.wait_for_block()

        return ac

    async def test_register(
        self, acnt0: pv.Account, new_maker_tok_ctrt_with_tok: pv.TokCtrtWithoutSplit
    ) -> pv.AtomicSwapCtrt:
        """
        test_register tests the method register.

        Args:
            acnt0 (pv.Account): The account of nonce 0.
            new_maker_tok_ctrt_with_tok (pv.TokCtrtWithoutSplit): The fixture that registers a new atomic swap contract and issues tokens right after it.

        Returns:
            pv.AtomicSwapCtrt: the AtomicSwapCtrt instance.
        """
        tc = new_maker_tok_ctrt_with_tok
        ac = await pv.AtomicSwapCtrt.register(acnt0, tc.tok_id.data)
        await cft.wait_for_block()

        assert (await ac.maker) == acnt0.addr
        assert (await ac.tok_id) == tc.tok_id

        return ac

    async def test_lock(
        self,
        acnt0: pv.Account,
        acnt1: pv.Account,
        new_maker_atomic_swap_ctrt: pv.AtomicSwapCtrt,
        new_taker_atomic_swap_ctrt: pv.AtomicSwapCtrt,
    ) -> None:
        """
        test_maker_lock_and_taker_lock tests the method maker_lock and taker_lock.

        Args:
            acnt0 (pv.Account): The account of nonce 0.
            acnt1 (pv.Account): The account of nonce 1.
            new_maker_atomic_swap_ctrt (pv.AtomicSwapCtrt): The fixture that registers a new atomic swap contract of maker's.
            new_taker_atomic_swap_ctrt (pv.AtomicSwapCtrt): The fixture that registers a new atomic swap contract of taker's.
        """
        maker_ctrt = new_maker_atomic_swap_ctrt
        taker_ctrt = new_taker_atomic_swap_ctrt
        api = acnt0.api

        maker_bal_init = await maker_ctrt.get_ctrt_bal(acnt0.addr.data)
        taker_bal_init = await taker_ctrt.get_ctrt_bal(acnt1.addr.data)

        # maker lock.
        maker_lock_amount = 10
        maker_lock_timestamp = int(time.time()) + 1800
        maker_puzzle_plain = "abc"
        puzzle_bytes1 = hs.sha256_hash(maker_puzzle_plain.encode("latin-1"))

        maker_lock_tx_info = await maker_ctrt.lock(
            acnt0,
            maker_lock_amount,
            acnt1.addr.data,
            puzzle_bytes1,
            maker_lock_timestamp,
        )
        await cft.wait_for_block()
        maker_lock_tx_id = maker_lock_tx_info["id"]
        await cft.assert_tx_success(api, maker_lock_tx_id)

        maker_swap_owner = await maker_ctrt.get_swap_owner(maker_lock_tx_id)
        assert maker_swap_owner.data == acnt0.addr.data

        maker_swap_recipient = await maker_ctrt.get_swap_recipient(maker_lock_tx_id)
        assert maker_swap_recipient.data == acnt1.addr.data

        maker_swap_amount = await maker_ctrt.get_swap_amount(maker_lock_tx_id)
        assert maker_swap_amount.amount == maker_lock_amount

        maker_swap_exp = await maker_ctrt.get_swap_expired_time(maker_lock_tx_id)
        assert maker_swap_exp.unix_ts == maker_lock_timestamp

        maker_swap_status = await maker_ctrt.get_swap_status(maker_lock_tx_id)
        assert maker_swap_status is True

        maker_puzzle = await maker_ctrt.get_swap_puzzle(maker_lock_tx_id)
        assert maker_puzzle == base58.b58encode(
            hs.sha256_hash(maker_puzzle_plain.encode("latin-1"))
        ).decode("latin-1")

        maker_bal_after_lock = await maker_ctrt.get_ctrt_bal(acnt0.addr.data)
        assert maker_bal_after_lock.amount == maker_bal_init.amount - 10

        # taker lock.
        puzzle_db_key = pv.AtomicSwapCtrt.DBKey.for_swap_puzzle(maker_lock_tx_id)
        resp = await acnt1._chain._api._ctrt.get_ctrt_data(
            maker_ctrt._ctrt_id.data, puzzle_db_key.b58_str
        )
        hashed_puzzle = resp["value"]

        puzzle_bytes2 = base58.b58decode(hashed_puzzle)

        taker_lock_timestamp = int(time.time()) + 1500
        taker_lock_tx_info = await taker_ctrt.lock(
            acnt1,
            5,
            acnt0.addr.data,
            puzzle_bytes2,
            taker_lock_timestamp,
        )
        await cft.wait_for_block()
        await cft.assert_tx_success(api, taker_lock_tx_info["id"])

        taker_bal_after_lock = await taker_ctrt.get_ctrt_bal(acnt1.addr.data)
        assert taker_bal_after_lock.amount == taker_bal_init.amount - 5

    async def test_solve(
        self,
        acnt0: pv.Account,
        acnt1: pv.Account,
        new_maker_atomic_swap_ctrt: pv.AtomicSwapCtrt,
        new_taker_atomic_swap_ctrt: pv.AtomicSwapCtrt,
    ) -> None:
        """
        test_maker_solve_and_taker_solve tests the method maker_solve and taker_solve.

        Args:
            acnt0 (pv.Account): The account of nonce 0.
            acnt1 (pv.Account): The account of nonce 1.
            new_maker_atomic_swap_ctrt (pv.AtomicSwapCtrt): The fixture that registers a new atomic swap contract of maker's.
            new_taker_atomic_swap_ctrt (pv.AtomicSwapCtrt): The fixture that registers a new atomic swap contract of taker's.
        """
        maker_ctrt = new_maker_atomic_swap_ctrt
        taker_ctrt = new_taker_atomic_swap_ctrt
        api = maker_ctrt.chain.api

        # maker lock.
        maker_lock_amount = 10
        maker_lock_timestamp = int(time.time()) + 1800
        maker_puzzle_plain = "abc"
        puzzle_bytes1 = hs.sha256_hash(maker_puzzle_plain.encode("latin-1"))

        maker_lock_tx_info = await maker_ctrt.lock(
            acnt0,
            maker_lock_amount,
            acnt1.addr.data,
            puzzle_bytes1,
            maker_lock_timestamp,
        )
        await cft.wait_for_block()
        maker_lock_tx_id = maker_lock_tx_info["id"]
        await cft.assert_tx_success(api, maker_lock_tx_id)

        # taker lock.
        puzzle_db_key = pv.AtomicSwapCtrt.DBKey.for_swap_puzzle(maker_lock_tx_id)
        resp = await acnt1._chain._api._ctrt.get_ctrt_data(
            maker_ctrt._ctrt_id.data, puzzle_db_key.b58_str
        )

        hashed_puzzle = resp["value"]
        puzzle_bytes2 = base58.b58decode(hashed_puzzle)

        taker_lock_timestamp = int(time.time()) + 1500
        taker_lock_tx_info = await taker_ctrt.lock(
            acnt1,
            5,
            acnt0.addr.data,
            puzzle_bytes2,
            taker_lock_timestamp,
        )
        await cft.wait_for_block()
        taker_lock_tx_id = taker_lock_tx_info["id"]
        await cft.assert_tx_success(api, taker_lock_tx_id)

        # maker solve
        maker_solve_tx_info = await taker_ctrt.solve(acnt0, taker_lock_tx_id, "abc")
        await cft.wait_for_block()
        maker_solve_id = maker_solve_tx_info["id"]
        await cft.assert_tx_success(api, maker_solve_id)

        dict_data = await acnt0.chain.api.tx.get_info(maker_solve_id)
        func_data = dict_data["functionData"]
        ds = de.DataStack.deserialize(base58.b58decode(func_data))
        revealed_secret = ds.entries[1].data.data.decode("latin-1")

        assert revealed_secret == "abc"

        taker_solve_tx_info = await maker_ctrt.solve(
            acnt1, maker_lock_tx_id, revealed_secret
        )
        await cft.wait_for_block()
        taker_solve_id = taker_solve_tx_info["id"]
        await cft.assert_tx_success(api, taker_solve_id)

    async def test_exp_withdraw(
        self,
        acnt0: pv.Account,
        acnt1: pv.Account,
        new_maker_atomic_swap_ctrt: pv.AtomicSwapCtrt,
    ) -> None:
        """
        test_exp_withdraw tests the method exp_withdraw.

        Args:
            acnt0 (pv.Account): The account of nonce 0.
            acnt1 (pv.Account): The account of nonce 1.
            new_maker_atomic_swap_ctrt (pv.AtomicSwapCtrt): The fixture that registers a new atomic swap contract of maker's.
        """
        maker_ctrt = new_maker_atomic_swap_ctrt
        api = maker_ctrt.chain.api

        maker_puzzle_plain = "abc"
        puzzle_bytes = hs.sha256_hash(maker_puzzle_plain.encode("latin-1"))

        maker_lock_tx_info = await maker_ctrt.lock(
            acnt0, 10, acnt1.addr.data, puzzle_bytes, int(time.time()) + 8
        )
        await cft.wait_for_block()
        maker_lock_id = maker_lock_tx_info["id"]
        await cft.assert_tx_success(api, maker_lock_id)

        bal_old = await maker_ctrt.get_ctrt_bal(acnt0.addr.data)

        await asyncio.sleep(10)  # wait until the lock is expired

        exp_withdraw_tx_info = await maker_ctrt.exp_withdraw(acnt0, maker_lock_id)
        await cft.wait_for_block()
        exp_withdraw_id = exp_withdraw_tx_info["id"]
        await cft.assert_tx_success(api, exp_withdraw_id)

        bal = await maker_ctrt.get_ctrt_bal(acnt0.addr.data)
        assert bal.amount == bal_old.amount + 10

    @pytest.mark.whole
    async def test_as_whole(
        self,
        acnt0: pv.Account,
        acnt1: pv.Account,
        new_maker_tok_ctrt_with_tok: pv.TokCtrtWithoutSplit,
        new_taker_atomic_swap_ctrt: pv.AtomicSwapCtrt,
    ) -> None:
        """
        test_as_whole tests methods of AtomicSwapCtrt as a whole so as to reduce resource consumption.

        Args:
            acnt0 (pv.Account): The account of nonce 0.
            acnt1 (pv.Account): The account of nonce 1.
            new_maker_tok_ctrt_with_tok (pv.TokCtrtWithoutSplit): The fixture that registers a new atomic swap contract and issues tokens right after it.
            new_taker_atomic_swap_ctrt (pv.AtomicSwapCtrt): The fixture that registers a new atomic swap contract of taker's.
        """
        api = acnt0.api

        maker_tc = new_maker_tok_ctrt_with_tok
        maker_ctrt = await self.test_register(acnt0, maker_tc)

        resp = await maker_tc.deposit(acnt0, maker_ctrt.ctrt_id.data, 100)
        await cft.wait_for_block()
        await cft.assert_tx_success(api, resp["id"])

        taker_ctrt = new_taker_atomic_swap_ctrt

        await self.test_lock(acnt0, acnt1, maker_ctrt, taker_ctrt)
        await self.test_solve(acnt0, acnt1, maker_ctrt, taker_ctrt)
        await self.test_exp_withdraw(acnt0, acnt1, maker_ctrt)
