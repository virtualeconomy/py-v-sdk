"""
curve_25519 contains functions for asymmertric cryptographic operations of curve25519
E.g. generate key pair, sign, verify signature
"""
from __future__ import annotations
import os
from typing import Optional

import axolotl_curve25519 as curve


def gen_pri_key(rand32: bytes) -> bytes:
    """
    gen_pri_key generates & returns a private key based on the given bytes

    Args:
        rand32 (bytes): The random 32-bytes bytes

    Returns:
        bytes: The generated private key
    """
    rand32 = bytes.fromhex(rand32.hex())
    return curve.generatePrivateKey(rand32)


def gen_pub_key(pri_key: bytes) -> bytes:
    """
    gen_pub_key generates & returns a public key based on the given private key

    Args:
        pri_key (bytes): The private key

    Returns:
        bytes: The generated public key
    """
    return curve.generatePublicKey(pri_key)


def sign(pri_key: bytes, msg: bytes, rand: Optional[bytes] = None) -> bytes:
    """
    sign signs the given message with the given private key

    Args:
        pri_key (bytes): The private key
        msg (bytes): The message to sign
        rand (bytes): The 64-bit random bytes

    Returns:
        bytes: The signature bytes
    """
    if not rand:
        rand = os.urandom(64)
    return curve.calculateSignature(rand, pri_key, msg)


def verify_sig(pub_key: bytes, msg: bytes, sig: bytes) -> bool:
    """
    verify_sig verifies the given signature with the public key & message

    Args:
        pub_key (bytes): The public key
        msg (bytes): The message to verify
        sig (bytes): The signature

    Returns:
        bool: If the signature is valid
    """
    return curve.verifySignature(pub_key, msg, sig) == 0
