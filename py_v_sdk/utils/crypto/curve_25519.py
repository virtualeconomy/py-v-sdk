from __future__ import annotations
import os
from typing import NamedTuple

import base58
import axolotl_curve25519 as curve


class KeyPair(NamedTuple):
    pub: bytes
    pri: bytes

    @property
    def pub_b58_str(self) -> str:
        return base58.b58encode(self.pub).decode("latin-1")

    @property
    def pri_b58_str(self) -> str:
        return base58.b58encode(self.pri).decode("latin-1")


def gen_pri_key(rand32: bytes) -> bytes:
    """
    gen_pri_key generates & returns a private key based on the given bytes

    Args:
        rand32 (bytes): The random 32-bytes bytes

    Returns:
        bytes: The generated private key
    """
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


def sign(pri_key: bytes, msg: bytes) -> bytes:
    """
    sign signs the given message with the given private key & 64-bytes random bytes

    Args:
        rand64 (bytes): The random 64-bytes bytes
        pri_key (bytes): The private key
        msg (bytes): The message to sign

    Returns:
        bytes: The signature bytes
    """
    rand64 = os.urandom(64)
    return curve.calculateSignature(rand64, pri_key, msg)


def verify_sig(pub_key: bytes, msg: bytes, sig: bytes) -> bool:
    """
    verify_sig verifies the given signature against the public key & message

    Args:
        pub_key (bytes): The public key
        msg (bytes): The message to verify
        sig (bytes): The signature

    Returns:
        bool: If the signature is valid
    """
    return curve.verifySignature(pub_key, msg, sig)
