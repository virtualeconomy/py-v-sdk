"""
test_acnt contains functional tests for Account.
"""

import uuid
import pytest

import py_v_sdk as pv
from . import conftest as cft


class TestAccount:
    """
    TestAccount is the collection of functional tests of Account.
    """

    @pytest.fixture
    def supernode_addr(self) -> str:
        return cft.SUPERNODE_ADDR

    async def test_pay(self, acnt0: pv.Account, acnt1: pv.Account):
        api = acnt0.api

        acnt0_bal_old = await acnt0.balance
        acnt1_bal_old = await acnt1.balance

        amount = pv.VSYS.for_amount(5)
        resp = await acnt0.pay(acnt1.addr.b58_str, amount.amount)
        await cft.wait_for_block()
        await cft.assert_tx_success(api, resp["id"])

        acnt0_bal = await acnt0.balance
        acnt1_bal = await acnt1.balance

        assert acnt0_bal == acnt0_bal_old - amount.data - pv.PaymentFee.DEFAULT
        assert acnt1_bal == acnt1_bal_old + amount.data

    async def test_lease(self, acnt0: pv.Account, supernode_addr: str):
        api = acnt0.api

        eff_bal_old = await acnt0.effective_balance

        amount = pv.VSYS.for_amount(5)
        resp = await acnt0.lease(supernode_addr, amount.amount)
        await cft.wait_for_block()
        await cft.assert_tx_success(api, resp["id"])

        assert (
            await acnt0.effective_balance
        ) == eff_bal_old - amount.data - pv.LeasingFee.DEFAULT

    async def test_cancel_lease(self, acnt0: pv.Account, supernode_addr: str):
        api = acnt0.api

        amount = pv.VSYS.for_amount(5)
        resp = await acnt0.lease(supernode_addr, amount.amount)
        await cft.wait_for_block()

        leasing_tx_id = resp["id"]
        await cft.assert_tx_success(api, leasing_tx_id)

        eff_bal_old = await acnt0.effective_balance

        resp = await acnt0.cancel_lease(leasing_tx_id)
        await cft.wait_for_block()
        await cft.assert_tx_success(api, resp["id"])

        eff_bal = await acnt0.effective_balance

        assert eff_bal == eff_bal_old + amount.data - pv.LeasingCancelFee.DEFAULT

    async def test_db_put(self, acnt0: pv.Account):
        api = acnt0.api

        db_key = "func_test"
        data = str(uuid.uuid4())

        resp = await acnt0.db_put(db_key, data)
        await cft.wait_for_block()
        await cft.assert_tx_success(api, resp["id"])

        resp = await api.db.get(acnt0.addr.b58_str, db_key)
        assert resp["data"] == data
