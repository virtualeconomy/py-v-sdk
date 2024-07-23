"""
model contains data model related resources.
"""
from __future__ import annotations
import abc
import time
from typing import Any, Union, Tuple, List, Optional
import struct

import base58

from py_vsys import chain as ch
from py_vsys.utils.crypto import hashes as hs
from py_vsys.utils.crypto import curve_25519 as curve


class Model(abc.ABC):
    """
    Model is the base class for data models that provides self-validation methods
    and other handy methods(e.g. converts bytes to base58 string).

    NOTE that the validate() method is deliberately called within the constructor so as
    to avoid accidental malformed data as much as possible.
    """

    def __init__(self, data: Any) -> None:
        """
        Args:
            data (Any): The data to contain.
        """
        self.data = data
        self.validate()

    @abc.abstractmethod
    def validate(self) -> None:
        """
        validate validates the containing data.
        """

    def __str__(self) -> str:
        """
        E.g. Str('hello')
        """
        cls_name = self.__class__.__name__
        return f"{cls_name}({self.data})"

    __repr__ = __str__

    def __eq__(self, other: Model) -> bool:
        return self.__class__ == other.__class__ and self.data == other.data


class Bytes(Model):
    """
    Bytes is the data model for bytes.
    """

    def __init__(self, data: bytes = b"") -> None:
        """
        Args:
            data (bytes, optional): The data to contain. Defaults to b"".
        """
        self.data = data
        self.validate()

    @property
    def b58_str(self) -> str:
        """
        b58_str returns the base58 string representation of the containing data.

        Returns:
            str: The base58 string representation.
        """
        return base58.b58encode(self.data).decode("latin-1")

    def validate(self) -> None:
        cls_name = self.__class__.__name__

        if not isinstance(self.data, bytes):
            raise TypeError(f"Data in {cls_name} must be bytes")

    @classmethod
    def from_b58_str(cls, s: str) -> Bytes:
        """
        from_b58_str creates a Bytes object from the given base58-encoded string.

        Args:
            s (str): the input base58 string.

        Returns:
            Bytes: the Bytes instance.
        """
        return cls(base58.b58decode(s))

    @classmethod
    def from_str(cls, s: str) -> Bytes:
        """
        from_str creates a Bytes object from the given string.
        Args:
            s (str): the input string.

        Returns:
            Bytes: the Bytes instance.
        """
        return cls(s.encode("latin-1"))


class AcntSeedHash(Bytes):
    """
    AcntSeedHash is the data model class for account seed hash.
    """

    BYTES_LEN = 32

    def validate(self) -> None:
        super().validate()

        cls_name = self.__class__.__name__

        if len(self.data) != self.BYTES_LEN:
            raise ValueError(
                f"Data in {cls_name} must be exactly {self.BYTES_LEN} bytes."
            )

    @property
    def key_pair(self):
        """
        getKeyPair generates a key pair.

        Returns:
            KeyPair: The generated key pair.
        """
        pri_key = curve.gen_pri_key(self.data)
        pub_key = curve.gen_pub_key(pri_key)

        return KeyPair(
            PubKey.from_bytes(pub_key),
            PriKey.from_bytes(pri_key),
        )


class Str(Model):
    """
    Str is the data model for string.
    """

    def __init__(self, data: str = "") -> None:
        """
        Args:
            data (str, optional): The data to contain. Defaults to "".
        """
        self.data = data
        self.validate()

    @classmethod
    def from_bytes(cls, b: bytes) -> Str:
        """
        from_bytes parses the given bytes and creates a Str.

        Args:
            b (bytes): The bytes to parse.

        Returns:
            Str: The Str instance.
        """
        return cls(b.decode("latin-1"))

    @property
    def bytes(self) -> bytes:
        """
        bytes returns the bytes representation of the containing data.

        Returns:
            bytes: The bytes representation.
        """
        return self.data.encode("latin-1")

    @property
    def b58_str(self) -> str:
        """
        b58_str returns the base58 string representation of the containing data.

        Returns:
            str: The base58 string representation.
        """
        return base58.b58encode(self.data).decode("latin-1")

    def validate(self) -> None:
        cls_name = self.__class__.__name__

        if not isinstance(self.data, str):
            raise TypeError(f"Data in {cls_name} must be a str")


class Seed(Str):
    WORD_CNT = 15

    def validate(self) -> None:
        super().validate()

    def get_acnt_seed_hash(self, nonce: Nonce) -> B58Str:
        """
        getAcntSeedHash gets account seed hash

        Args:
            nonce (Nonce): The nonce of the account.

        Returns:
            B58Str: The B58Str instance.
        """
        b = hs.sha256_hash(
            hs.keccak256_hash(
                hs.blake2b_hash(f"{nonce.data}{self.data}".encode("latin-1"))
            )
        )
        return AcntSeedHash(b)


class B58Str(Str):
    """
    B58Str is the data model for base58 string.
    """

    @classmethod
    def from_bytes(cls, b: bytes) -> B58Str:
        """
        from_bytes parses the given bytes and creates a B58Str.

        Args:
            b (bytes): The bytes to parse.

        Returns:
            B58Str: The B58Str instance.
        """
        return cls(base58.b58encode(b).decode("latin-1"))

    @property
    def bytes(self) -> bytes:
        """
        bytes returns the bytes representation of the containing data.

        Returns:
            bytes: The bytes representation.
        """
        return base58.b58decode(self.data)

    def validate(self) -> None:
        super().validate()
        cls_name = self.__class__.__name__

        try:
            self.bytes
        except ValueError:
            raise ValueError(f"Data in {cls_name} must be base58-decodable")


class FixedSizeB58Str(B58Str):
    """
    FixedSizeB58Str is the data model for fixed-size base58 string.
    """

    BYTES_LEN = 0

    def validate(self) -> None:
        super().validate()
        cls_name = self.__class__.__name__

        if not len(self.bytes) == self.BYTES_LEN:
            raise ValueError(
                f"Data in {cls_name} must be exactly {self.BYTES_LEN} bytes after base58 decode"
            )


class Addr(FixedSizeB58Str):
    """
    Addr is the data model for an address.
    """

    VER = 5
    VER_BYTES_LEN = 1
    CHAIN_ID_BYTES_LEN = 1
    PUB_KEY_HASH_BYTES_LEN = 20
    CHECKSUM_BYTES_LEN = 4
    BYTES_LEN = (
        VER_BYTES_LEN + CHAIN_ID_BYTES_LEN + PUB_KEY_HASH_BYTES_LEN + CHECKSUM_BYTES_LEN
    )

    @property
    def version(self) -> int:
        """
        version returns the version of the address.

        Returns:
            int: The version.
        """
        return self.bytes[0]

    @property
    def chain_id(self) -> str:
        """
        chain_id returns the chain ID of the address.

        Returns:
            str: The chain ID.
        """
        return chr(self.bytes[1])

    @property
    def pub_key_hash(self) -> bytes:
        """
        pub_key_hash returns the hash of the public key of the address.

        Returns:
            bytes: The hash.
        """
        prev_len = self.VER_BYTES_LEN + self.CHAIN_ID_BYTES_LEN
        b = self.bytes[prev_len:]
        return b[: self.PUB_KEY_HASH_BYTES_LEN]

    @property
    def checksum(self) -> bytes:
        """
        checksum returns the checksum of the address.

        Returns:
            bytes: The checksum.
        """
        return self.bytes[-self.CHECKSUM_BYTES_LEN :]

    def must_on(self, chain: ch.Chain):
        """
        must_on asserts that the address must be on the given chain.

        Args:
            chain (ch.Chain): The chain object.

        Raises:
            ValueError: If the address is not on the given chain.
        """
        if self.chain_id != chain.chain_id.value:
            raise ValueError(
                f"Addr is not on the chain. The Addr has chain_id '{self.chain_id}' while the chain expects '{chain.chain_id.value}'"
            )

    @classmethod
    def from_pub_key(cls, pub_key: PubKey, chain_id: ch.ChainID) -> B58Str:
        """
        from_pub_key creates a new Addr instance from the given public key & chain ID.

        Args:
            pub_key (PubKey): The public key.
            chain_id (ch.ChainID): The chain ID.

        Returns:
            Addr: The generated address.
        """

        def ke_bla_hash(b: bytes) -> bytes:
            return hs.keccak256_hash(hs.blake2b_hash(b))

        raw_addr: str = (
            chr(cls.VER)
            + chain_id.value
            + ke_bla_hash(pub_key.bytes).decode("latin-1")[:20]
        )

        checksum: str = ke_bla_hash(raw_addr.encode("latin-1")).decode("latin-1")[:4]

        b = bytes((raw_addr + checksum).encode("latin-1"))
        return cls.from_bytes(b)

    def validate(self) -> None:
        super().validate()
        cls_name = self.__class__.__name__

        if self.version != self.VER:
            raise ValueError(f"Data in {cls_name} has invalid address version")

        chain_id_valid = any([self.chain_id == c.value for c in ch.ChainID])
        if not chain_id_valid:
            raise ValueError(f"Data in {cls_name} has invalid chain_id")

        def ke_bla_hash(b: bytes) -> bytes:
            return hs.keccak256_hash(hs.blake2b_hash(b))

        cl = self.CHECKSUM_BYTES_LEN
        if self.checksum != ke_bla_hash(self.bytes[:-cl])[:cl]:
            raise ValueError(f"Data in {cls_name} has invalid checksum")

    @classmethod
    def from_bytes_md(cls, b: Bytes) -> Addr:
        """
        from_bytes_md contructs an Addr object from the given Bytes object.

        Args:
            b (Bytes): The given Bytes object.

        Returns:
            Addr: The Addr object.
        """
        return cls(b.b58_str)


class CtrtMetaBytes:
    """
    CtrtMetaBytes is the helper data container for bytes used in contract meta data
    with handy methods.
    """

    def __init__(self, data: bytes = b"") -> None:
        """
        Args:
            data (bytes, optional): The data to contain. Defaults to b"".
        """
        self.data = data

    @classmethod
    def deserialize(cls, b: bytes) -> CtrtMetaBytes:
        """
        deserialize deserializes the given bytes and creates a CtrtMetaBytes object.

        Args:
            b (bytes): The bytes to deserialize.

        Returns:
            CtrtMetaBytes: The CtrtMetaBytes object created by deserialization.
        """
        l = struct.unpack(">H", b[:2])[0]
        return cls(b[2 : 2 + l])

    @property
    def len_bytes(self) -> bytes:
        """
        len_bytes returns the length in bytes of the containing data.

        Returns:
            bytes: The length in bytes.
        """
        return struct.pack(">H", len(self.data))

    def serialize(self) -> bytes:
        """
        serialize serializes CtrtMetaBytes object to bytes.

        Returns:
            bytes: The serialization result.
        """
        return self.len_bytes + self.data


class CtrtMetaBytesList:
    """
    CtrtMetaBytesList is a collection of CtrtMetaBytes
    """

    def __init__(self, *items: Tuple[CtrtMetaBytes]) -> None:
        """
        Args:
            *items (Tuple[CtrtMetaBytes]): CtrtMetaBytes objects to contain
        """
        self.items: List[CtrtMetaBytes] = list(items)

    @classmethod
    def deserialize(cls, b: bytes, with_bytes_len: bool = True) -> CtrtMetaBytesList:
        """
        deserialize deserializes the given bytes and creates a BytesList object.

        Args:
            b (bytes): The bytes to deserialize.
            with_bytes_len (bool, optional): If the first 2 bytes of the given data
                should be treated as the meta data that indicates the length for the data.
                Defaults to True.

        Returns:
            CtrtMetaBytesList: The CtrtMetaBytesList object created by deserialization.
        """
        if with_bytes_len:
            l = struct.unpack(">H", b[:2])[0]
            b = b[2 : 2 + l]

        items_cnt = struct.unpack(">H", b[:2])[0]
        b = b[2:]
        items = []
        for _ in range(items_cnt):
            l = struct.unpack(">H", b[:2])[0]
            item = CtrtMetaBytes.deserialize(b)
            items.append(item)
            b = b[2 + l :]

        return cls(*items)

    def serialize(self, with_bytes_len: bool = True) -> bytes:
        """
        serialize serializes CtrtMetaBytesList object to bytes.

        Args:
            with_bytes_len (bool, optional): If the 2-bytes meta data that indicates
                the length of the data should be prepended.
                Defaults to True.

        Returns:
            bytes: The serialization result.
        """
        b = struct.pack(">H", len(self.items))

        for i in self.items:
            b += i.serialize()

        if with_bytes_len:
            b = struct.pack(">H", len(b)) + b

        return b


class CtrtMeta:
    LANG_CODE_BYTE_LEN = 4
    LANG_VER_BYTE_LEN = 4
    TOKEN_ADDR_VER = -124
    CTRT_ADDR_VER = 6
    CHECKSUM_LEN = 4
    TOKEN_IDX_BYTES_LEN = 4

    def __init__(
        self,
        lang_code: str,
        lang_ver: int,
        triggers: CtrtMetaBytesList,
        descriptors: CtrtMetaBytesList,
        state_vars: CtrtMetaBytesList,
        state_map: CtrtMetaBytesList,
        textual: CtrtMetaBytesList,
    ) -> None:
        """
        Args:
            lang_code (str): The language code of the contract. E.g. "vdds".
            lang_ver (int): The language version of the contract. E.g. 1
            triggers (CtrtMetaBytesList): The triggers of the contract.
            descriptors (CtrtMetaBytesList): The descriptors of the contract.
            state_vars (CtrtMetaBytesList): The state variables of the contract.
            state_map (CtrtMetaBytesList): The state map of the contract.
            textual (CtrtMetaBytesList): The textual of the contract.
        """
        self.lang_code = lang_code
        self.lang_ver = lang_ver
        self.triggers = triggers
        self.descriptors = descriptors
        self.state_vars = state_vars
        self.state_map = state_map
        self.textual = textual

    @classmethod
    def from_b58_str(cls, b58_str: str) -> CtrtMeta:
        """
        from_b58_str creates a CtrtMeta object from the given base58 string.

        Args:
            b58_str (str): The base58 string to parse.

        Returns:
            CtrtMeta: The result CtrtMeta object.
        """
        b = base58.b58decode(b58_str)
        return cls.deserialize(b)

    @classmethod
    def deserialize(cls, b: bytes) -> CtrtMeta:
        """
        deserialize deserializes the given bytes to a CtrtMeta object.

        Args:
            b (bytes): The bytes to deserialize.

        Returns:
            CtrtMeta: The result CtrtMeta object.
        """

        def parse_len(b: bytes) -> int:
            """
            parse_len unpacks the given 2 bytes as an unsigned short integer.

            Args:
                b (bytes): The bytes to unpack.

            Returns:
                int: The unpacked value.
            """
            return struct.unpack(">H", b)[0]

        lang_code = b[:4].decode("latin-1")
        b = b[4:]

        lang_ver = struct.unpack(">I", b[:4])[0]
        b = b[4:]

        l = parse_len(b[:2])
        triggers = CtrtMetaBytesList.deserialize(b)
        b = b[2 + l :]

        l = parse_len(b[:2])
        descriptors = CtrtMetaBytesList.deserialize(b)
        b = b[2 + l :]

        l = parse_len(b[:2])
        state_vars = CtrtMetaBytesList.deserialize(b)
        b = b[2 + l :]

        if lang_ver == 1:
            state_map = CtrtMetaBytesList()
        else:
            l = parse_len(b[:2])
            state_map = CtrtMetaBytesList.deserialize(b)
            b = b[2 + l :]

        textual = CtrtMetaBytesList.deserialize(b, with_bytes_len=False)

        return cls(
            lang_code, lang_ver, triggers, descriptors, state_vars, state_map, textual
        )

    def serialize(self) -> bytes:
        """
        serialize serializes CtrtMeta to a bytes.

        Returns:
            bytes: The serialization result.
        """
        stmap_bytes = b"" if self.lang_ver == 1 else self.state_map.serialize()
        b = (
            self.lang_code.encode("latin-1")
            + struct.pack(">I", self.lang_ver)
            + self.triggers.serialize()
            + self.descriptors.serialize()
            + self.state_vars.serialize()
            + stmap_bytes
            + self.textual.serialize(with_bytes_len=False)
        )
        return b


class CtrtID(FixedSizeB58Str):
    """
    CtrtID is the data model for contract ID.
    """

    BYTES_LEN = 26

    def get_tok_id(self, tok_idx: int) -> TokenID:
        """
        get_tok_id computes the token ID based on the given token index.

        Args:
            tok_idx (int): The token index.

        Returns:
            TokenID: The token ID.
        """
        # TokenIdx(tok_idx) # for validation

        b = self.bytes
        raw_ctrt_id = b[1 : (len(b) - CtrtMeta.CHECKSUM_LEN)]
        ctrt_id_no_checksum = (
            struct.pack("<b", CtrtMeta.TOKEN_ADDR_VER)
            + raw_ctrt_id
            + struct.pack(">I", tok_idx)
        )
        h = hs.keccak256_hash(hs.blake2b_hash(ctrt_id_no_checksum))

        tok_id_bytes = base58.b58encode(
            ctrt_id_no_checksum + h[: CtrtMeta.CHECKSUM_LEN]
        )

        tok_id = tok_id_bytes.decode("latin-1")
        return TokenID(tok_id)


class TokenID(FixedSizeB58Str):
    """
    TokenID is the data model for token ID.
    """

    BYTES_LEN = 30
    MAINNET_VSYS_TOK_ID = "TWatCreEv7ayv6iAfLgke6ppVV33kDjFqSJn8yicf"
    TESTNET_VSYS_TOK_ID = "TWuKDNU1SAheHR99s1MbGZLPh1KophEmKk1eeU3mW"

    @property
    def is_vsys_tok(self) -> bool:
        return self.is_testnet_vsys_tok or self.is_mainnet_vsys_tok

    @property
    def is_mainnet_vsys_tok(self) -> bool:
        return self.data == self.MAINNET_VSYS_TOK_ID

    @property
    def is_testnet_vsys_tok(self) -> bool:
        return self.data == self.TESTNET_VSYS_TOK_ID

    def get_ctrt_id(self):
        """
        get_ctrt_id computes the contract ID from token ID.

        Returns:
            CtrtID: The contract ID.
        """
        b = base58.b58decode(self.data)
        raw_ctrt_id = b[
            1 : (len(b) - CtrtMeta.TOKEN_IDX_BYTES_LEN - CtrtMeta.CHECKSUM_LEN)
        ]
        ctrt_id_no_checksum = struct.pack("<b", CtrtMeta.CTRT_ADDR_VER) + raw_ctrt_id

        h = hs.keccak256_hash(hs.blake2b_hash(ctrt_id_no_checksum))

        ctrt_id_bytes = base58.b58encode(
            ctrt_id_no_checksum + h[: CtrtMeta.CHECKSUM_LEN]
        )
        ctrt_id_str = ctrt_id_bytes.decode("latin1")
        return CtrtID(ctrt_id_str)


class TXID(FixedSizeB58Str):
    """
    TXID is the data model for transaction ID.
    """

    BYTES_LEN = 32


class PubKey(FixedSizeB58Str):
    """
    PubKey is the data model for public key.
    """

    BYTES_LEN = 32

    def verify(self, msg: bytes, sig: bytes) -> bool:
        """
        verify verifies the given signature & message.

        Args:
            msg: (bytes): The message to verify.
            sig: (bytes): The signature to verify.
        
        Returns:
            bool: If the signature is valid.
        """
        return curve.verify_sig(self.bytes, msg, sig)


class PriKey(FixedSizeB58Str):
    """
    PriKey is the data model for private key.
    """

    BYTES_LEN = 32

    def sign(self, msg: bytes, rand: Optional[bytes]) -> Bytes:
        """
        sign signs the given message & return the signature.

        Args:
            msg: (bytes): the message to sign.
        
        Returns:
            Bytes: The signature of the given message.
        """

        b = curve.sign(self.bytes, msg, rand)
        return Bytes(b)


class Int(Model):
    """
    Int is the data model for an integer.
    """

    def __init__(self, data: int = 0) -> None:
        """
        Args:
            data (int, optional): The data to contain. Defaults to 0.
        """
        self.data = data
        self.validate()

    def validate(self) -> None:
        cls_name = self.__class__.__name__
        if not isinstance(self.data, int):
            raise TypeError(f"Data in {cls_name} must be an int")


class NonNegativeInt(Int):
    """
    NonNegativeInt is the data model for a non-negative integer.
    """

    def validate(self) -> None:
        super().validate()
        cls_name = self.__class__.__name__

        if not self.data >= 0:
            raise ValueError(f"Data in {cls_name} must be non negative")


class TokenIdx(NonNegativeInt):
    """
    TokenIdx is the data model for token index.
    """

    pass


class Nonce(NonNegativeInt):
    """
    Nonce is the data model for nonce (used with seed for an account).
    """

    pass


class VSYSTimestamp(NonNegativeInt):
    """
    VSYSTimestamp is the data model for the timestamp used in VSYS.
    """

    SCALE = 1_000_000_000

    @classmethod
    def from_unix_ts(cls, ux_ts: Union[int, float]) -> VSYSTimestamp:
        """
        from_unix_ts creates a new VSYSTimestamp from the given UNIX timestamp at seconds.

        Args:
            ux_ts (Union[int, float]): The UNIX timestamp.

        Raises:
            TypeError: If the type of the given UNIX timestamp is neither int nor float.
            ValueError: If the given UNIX timestamp is not positive.

        Returns:
            VSYSTimestamp: The VSYSTimestamp.
        """
        if not (isinstance(ux_ts, int) or isinstance(ux_ts, float)):
            raise TypeError("ux_ts must be an int or float")

        return cls(int(ux_ts * cls.SCALE))

    @classmethod
    def now(cls) -> VSYSTimestamp:
        """
        now creates a new VSYSTimestamp for current time.

        Returns:
            VSYSTimestamp: The VSYSTimestamp.
        """
        return cls(int(time.time() * cls.SCALE))

    @property
    def unix_ts(self) -> float:
        return self.data / self.SCALE

    def validate(self) -> None:
        super().validate()
        cls_name = self.__class__.__name__

        if not (self.data == 0 or self.data >= self.SCALE):
            raise ValueError(
                f"Data in {cls_name} must be either be 0 or equal or greater than {self.SCALE}"
            )


class Token(NonNegativeInt):
    """
    Token is the data model for tokens.
    """

    def __init__(self, data: int = 0, unit: int = 0) -> None:
        """
        Args:
            data (int, optional): The data to contain. Defaults to 0.
            unit (int, optional): The unit of the token. Defaults to 0.
        """
        super().__init__(data)
        self.unit = unit

    @property
    def amount(self) -> float:
        """
        amount returns the amount of Token the Token object represents.

        Returns:
            float: The amount of Token.
        """
        return self.data / self.unit

    @classmethod
    def for_amount(cls, amount: Union[int, float], unit: int) -> Token:
        """
        for_amount creates a new Token where the amount is equal to the given amount.

        Args:
            amount (Union[int, float]): The amount.

        Returns:
            Token: The Token.
        """
        data = amount * unit

        if int(data) < data:
            raise ValueError(
                f"Invalid amount for {cls.__name__}: {amount}. The minimal valid amount granularity is {1 / unit}"
            )

        return cls(int(data), unit)


class VSYS(NonNegativeInt):
    """
    VSYS is the data model for VSYS(the native token on VSYS blockchain).
    """

    UNIT = 1_00_000_000

    @property
    def amount(self) -> float:
        """
        amount returns the amount of VSYS coins the VSYS object represents.

        Returns:
            float: The amount of VSYS coins.
        """
        return self.data / self.UNIT

    @classmethod
    def for_amount(cls, amount: Union[int, float]) -> VSYS:
        """
        for_amount creates a new VSYS where the amount is equal to the given amount.

        Args:
            amount (Union[int, float]): The amount.

        Returns:
            VSYS: The VSYS.
        """
        data = amount * cls.UNIT

        if int(data) < data:
            raise ValueError(
                f"Invalid amount for {cls.__name__}: {amount}. The minimal valid amount granularity is {1 / cls.UNIT}"
            )

        return cls(int(data))

    def __mul__(self, factor: Union[int, float]) -> VSYS:
        """
        __mul__ defines the behaviour of the '*' operator.

        E.g.
            v1 = VSYS.for_amount(1)
            v20 = v1 * 20
            v2 = v20 * 0.1

        Args:
            factor (Union[int, float]): The factor to multiply.

        Returns:
            VSYS: The result of the multiplication.
        """
        return self.__class__(int(self.data * factor))


class Fee(VSYS):
    """
    Fee is the data model for transaction fee.
    """

    DEFAULT = int(VSYS.UNIT * 0.1)

    def __init__(self, data: int = 0) -> None:
        """
        Args:
            data (int, optional): The data to contain. Defaults to VSYS.UNIT * 0.1.
        """
        if data == 0:
            data = self.DEFAULT
        super().__init__(data)

    def validate(self) -> None:
        super().validate()
        cls_name = self.__class__.__name__

        if not self.data >= self.DEFAULT:
            raise ValueError(
                f"Data in {cls_name} must be equal or greater than {self.DEFAULT}"
            )


class PaymentFee(Fee):
    """
    PaymentFee is the data model for the fee of a transaction where the type is Payment.
    """

    pass


class LeasingFee(Fee):
    """
    LeasingFee is the data model for the fee of a transaction where the type is Leasing.
    """

    pass


class LeasingCancelFee(Fee):
    """
    LeasingCancelFee is the data model for the fee of a transaction where the type is Leasing Cancel.
    """

    pass


class RegCtrtFee(Fee):
    """
    RegCtrtFee is the data model for the fee of a transaction where the type is Register Contract.
    """

    DEFAULT = VSYS.UNIT * 100


class ExecCtrtFee(Fee):
    """
    ExecCtrtFee is the data model for the fee of a transaction where the type is Execute Contract.
    """

    DEFAULT = int(VSYS.UNIT * 0.3)


class ContendSlotsFee(Fee):
    """
    ContendSlotsFee is the data model for the fee of a transaction where the type is Contend Slots.
    """

    DEFAULT = VSYS.UNIT * 50_000


class DBPutFee(Fee):
    """
    DBPutFee is the data model for the fee of a transaction where the type is DB Put.
    """

    DEFAULT = VSYS.UNIT


class Bool(Model):
    """
    Bool is the data model for a boolean value.
    """

    def __init__(self, data: bool = False) -> None:
        """
        Args:
            data (bool, optional): The data to contain. Defaults to False.
        """
        self.data = data
        self.validate()

    def validate(self) -> None:
        cls_name = self.__class__.__name__

        if not isinstance(self.data, bool):
            raise TypeError(f"Data in {cls_name} must be a bool")


class KeyPair:
    """
    KeyPair is the data model for a key pair(public / private keys).
    """

    def __init__(self, pub_key: PubKey, pri_key: PriKey) -> None:
        """
        Args:
            pub_key (PubKey): The public key.
            pri_key (PriKey): The private key.
        """
        self.pub = pub_key
        self.pri = pri_key

        self.validate()

    def validate(self) -> None:
        msg = bytes("abc", "utf-8")
        sig = curve.sign(self.pri.bytes, msg)

        is_valid = curve.verify_sig(self.pub.bytes, msg, sig)

        if not is_valid:
            raise ValueError("Public key & private key do not match.")
