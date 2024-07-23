"""
test_api contains functional tests for py_vsys/api.py
"""
import aiohttp

import py_vsys as pv


class TestAPIGrp:
    """
    TestAPIGrp tests pv.APIGrp
    """

    class MockAPIGrp(pv.APIGrp):
        """
        MockAPIGrp is the test subclass of pv.APIGrp
        """

        PREFIX = "TEST"

    async def test_make_url(self, host: str) -> None:
        """
        test_make_url tests pv.APIGrp._make_url

        Args:
            host (str): The node api host.
        """
        sess = aiohttp.ClientSession(base_url=host)
        obj = self.MockAPIGrp(sess)
        edpt = "EDPT"
        assert obj._make_url(edpt) == self.MockAPIGrp.PREFIX + edpt

    async def test_get(self, host: str) -> None:
        """
        test_get tests pv.APIGrp._get

        Args:
            host (str): The node api host.
        """
        self.MockAPIGrp.PREFIX = "/blocks"

        sess = aiohttp.ClientSession(base_url=host)
        edpt = "/height"

        resp = await self.MockAPIGrp(sess)._get(edpt)
        assert resp["height"] > 0

    async def test_post(self, host: str) -> None:
        """
        test_post tests pv.APIGrp._post

        Args:
            host (str): The node api host.
        """
        self.MockAPIGrp.PREFIX = "/utils"

        sess = aiohttp.ClientSession(base_url=host)
        edpt = "/hash/fast"

        raw = "hello"
        resp = await self.MockAPIGrp(sess)._post(edpt, raw)
        assert resp["hash"] == "4PNCZERNLKAqwSYHhZpb7B4GE34eiYDPXGgeNKWNNaBp"
