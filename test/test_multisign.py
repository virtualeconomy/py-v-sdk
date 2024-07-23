"""
test_api contains demonstrating tests for py_vsys/multisign.py
"""

import base58
import pytest
import axolotl_curve25519 as curve

import py_vsys as pv


PRI_KEY_1 = "EV9ADJzYKZpk4MjxEkXxDSfRRSzBFnA9LEQNbepKZRFc"
PRI_KEY_2 = "3hQRGJkqKFbks77cZ12ugHxDtbweH3EZjhfVzfr4RqPs"

MSG = b"test"
RAND = b'\xb2\x98\xc9\xd1\x94\x7f\xcb\x83s\xa2\x00#+oly\xf7\x85H\x14\xc7Nfa;.\xa0\xc8C\xbd\xadP\xcb<\x83s\x94/\n\x8a\n\xaa\xda\x8c#\x8c\x01\x12yUOtY\xba\xb5`\xb6\xebC\x99*\xaf8\x86'


@pytest.fixture
def mulpk1():
    """
    mulpk1 is the test MultiSignPriKey No.1
    """
    return pv.MultiSignPriKey(
        base58.b58decode(PRI_KEY_1)
    )


@pytest.fixture
def mulpk2():
    """
    mulpk2 is the test MultiSignPriKey No.2
    """
    return pv.MultiSignPriKey(
        base58.b58decode(PRI_KEY_2)
    )


def test_multisign_one_key(mulpk1: pv.MultiSignPriKey):
    """
    test_multisign_one_key tests the case where only a single private key is used
    for the multisign procedure. The signature should match the one produced by signing
    with the private key directly.

    Args:
        mulpk1 (pv.MultiSignPriKey): The pv.MultiSignPriKey for the private key.
    """
    A = mulpk1.A
    allAs = (A,)

    xA = mulpk1.get_xA(A)
    unionA = pv.MultiSign.get_unionA(xA)

    R = mulpk1.get_R(MSG, RAND)
    unionR = pv.MultiSign.get_unionR(R)

    sub_sig = mulpk1.sign(MSG, RAND, unionA, unionR, allAs)
    mul_sig = pv.MultiSign.get_sig(unionA, unionR, (sub_sig,))

    bpA = mulpk1.get_bpA(A)
    mul_pub = pv.MultiSign.get_pub(bpA)

    raw_sig = curve.calculateSignature(RAND, mulpk1.pri_key, MSG)
    assert mul_sig == raw_sig

    raw_pub = curve.generatePublicKey(mulpk1.pri_key)
    assert mul_pub == raw_pub

    valid = curve.verifySignature(mul_pub, MSG, mul_sig) == 0
    assert valid is True


def test_multisign_two_keys(
    mulpk1: pv.MultiSignPriKey,
    mulpk2: pv.MultiSignPriKey,
):
    """
    test_multisign_two_key tests the case where 2 private keys are used
    for the multisign procedure. 

    Args:
        mulpk1 (pv.MultiSignPriKey): The pv.MultiSignPriKey for the private key 1.
        mulpk2 (pv.MultiSignPriKey): The pv.MultiSignPriKey for the private key 2.
    """

    A1 = mulpk1.A
    A2 = mulpk2.A
    allAs = (A1, A2)

    xA1 = mulpk1.get_xA(*allAs)
    xA2 = mulpk2.get_xA(*allAs)
    xAs = (xA1, xA2)
    unionA = pv.MultiSign.get_unionA(*xAs)

    R1 = mulpk1.get_R(MSG, RAND)
    R2 = mulpk2.get_R(MSG, RAND)
    Rs = (R1, R2)
    unionR = pv.MultiSign.get_unionR(*Rs)

    sub_sig1 = mulpk1.sign(MSG, RAND, unionA, unionR, allAs)
    sub_sig2 = mulpk2.sign(MSG, RAND, unionA, unionR, allAs)
    sigs = (sub_sig1, sub_sig2)
    mul_sig = pv.MultiSign.get_sig(unionA, unionR, sigs)

    bpA1 = mulpk1.get_bpA(*allAs)
    bpA2 = mulpk2.get_bpA(*allAs)
    bpAs = (bpA1, bpA2)
    mul_pub = pv.MultiSign.get_pub(*bpAs)

    valid = curve.verifySignature(mul_pub, MSG, mul_sig) == 0
    assert valid is True    
