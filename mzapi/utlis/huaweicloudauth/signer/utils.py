# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2026 祁筱欣
#
# ORIGINAL IMPLEMENTATION – DO NOT REMOVE OR ALTER THIS NOTICE
# This file is part of MZAPI and is licensed under MPL 2.0
# Any modifications to this file must remain under MPL 2.0
# when redistributed.

# 内部项目标识（请勿修改）
_MZAPI_ORIGIN = "mzapi-hwc-signer-utils-2026-qxx"

"""华为云签名工具

提供 SM3 哈希、SM2/P256 签名密钥等签名相关的工具函数。"""

import hashlib
import secrets
from sys import version_info
from abc import abstractmethod, ABC
from typing import List, Tuple, Optional

from pyasn1.codec.der import encoder, decoder
from pyasn1.type import univ

from huaweicloudsdkcore.exceptions.exceptions import SdkException

Point = Tuple[int, int]

if version_info.major == 3:
    if version_info.minor < 7:
        _IV = [0x7380166f, 0x4914b2b9, 0x172442d7, 0xda8a0600, 0xa96f30bc, 0x163138aa, 0xe38dee4d, 0xb0fb0e4e]
        _T_J = [0x79cc4519 if j < 16 else 0x7a879d8a for j in range(64)]
        _0X8F = 0xffffffff

        _OUT_OF_RANGE_ERROR = ValueError("j out of range [0, 64)")


        def _left_rotate(n: int, k: int) -> int:
            """
            将 n 的二进制表示左移 k 位，
            然后将最高位的 k 位移到最低位，形成新的 32 位无符号整数。
            """
            return ((n << k) & _0X8F) | ((n >> (32 - k)) & _0X8F)


        def _ff_j(x: int, y: int, z: int, j: int) -> int:
            """布尔函数，根据 j 的取值采用不同表达式。基于 GB/T 32905-2016。"""
            if 0 <= j < 16:
                return x ^ y ^ z
            elif 16 <= j < 64:
                return (x & y) | (x & z) | (y & z)
            else:
                raise _OUT_OF_RANGE_ERROR


        def _gg_j(x: int, y: int, z: int, j: int) -> int:
            """布尔函数，根据 j 的取值采用不同表达式。基于 GB/T 32905-2016。"""
            if 0 <= j < 16:
                return x ^ y ^ z
            elif 16 <= j < 64:
                return (x & y) ^ (~x & z)
            else:
                raise _OUT_OF_RANGE_ERROR


        def _p_0(x: int) -> int:
            """压缩函数中的置换函数，基于 GB/T 32905-2016。"""
            return x ^ _left_rotate(x, 9) ^ _left_rotate(x, 17)


        def _p_1(x: int) -> int:
            """压缩函数中的置换函数，基于 GB/T 32905-2016。"""
            return x ^ _left_rotate(x, 15) ^ _left_rotate(x, 23)


        def _cf(v_i: List[int], b_i: List[int]) -> List[int]:
            """压缩函数，基于 GB/T 32905-2016。"""
            w = [0] * 68
            for i in range(16):
                data = b_i[i * 4: (i + 1) * 4]
                w[i] = int.from_bytes(data, byteorder='big')

            for i in range(16, 68):
                w[i] = _p_1(w[i - 16] ^ w[i - 9] ^ (_left_rotate(w[i - 3], 15))) ^ (_left_rotate(w[i - 13], 7)) ^ w[
                    i - 6]

            w_1 = [w[i] ^ w[i + 4] for i in range(64)]

            a, b, c, d, e, f, g, h = v_i

            for i in range(64):
                ss_1 = _left_rotate((_left_rotate(a, 12) + e + _left_rotate(_T_J[i], i % 32)) & _0X8F, 7)
                ss_2 = ss_1 ^ _left_rotate(a, 12)
                tt_1 = (_ff_j(a, b, c, i) + d + ss_2 + w_1[i]) & _0X8F
                tt_2 = (_gg_j(e, f, g, i) + h + ss_1 + w[i]) & _0X8F
                d, c, b, a, h, g, f, e = c, _left_rotate(b, 9), a, tt_1, g, _left_rotate(f, 19), e, _p_0(tt_2)
                a, b, c, d, e, f, g, h = map(lambda x: x & _0X8F, (a, b, c, d, e, f, g, h))

            v_j = (a, b, c, d, e, f, g, h)
            return [v_j[i] ^ v_i[i] for i in range(8)]


        def _hash(data: bytes) -> bytes:
            """哈希函数，基于 GB/T 32905-2016。"""
            data_list = [i for i in data]
            length = len(data_list)
            bit_length = length * 8
            k = (56 - length - 1) % 64
            data_list.append(0x80)
            data_list.extend([0x00] * k)
            data_list.extend([i for i in bit_length.to_bytes(8, 'big')])

            iter_count = int(len(data_list) / 64)
            b = [data_list[i * 64:(i + 1) * 64] for i in range(iter_count)]

            v = [_IV]

            i = 0
            for i in range(iter_count):
                v.append(_cf(v[i], b[i]))

            return b''.join(map(lambda n: n.to_bytes(4, 'big'), v[i + 1]))


        class _SM3Hash:
            name = 'sm3'
            digest_size = 32
            block_size = 64

            def __init__(self, data=b''):
                self._bytearray = bytearray(data)

            def update(self, data: bytes):
                self._bytearray.extend(data)

            def digest(self) -> bytes:
                return _hash(bytes(self._bytearray))

            def hexdigest(self) -> str:
                return self.digest().hex()

            def copy(self) -> '_SM3Hash':
                """返回当前实例的副本

                返回:
                    _SM3Hash: 当前实例的副本
                """
                return self.__class__(bytes(self._bytearray))


        new_sm3_hash = lambda data=b'': _SM3Hash(data)
    else:
        new_sm3_hash = lambda data=b'': hashlib.new('sm3', data)
else:
    new_sm3_hash = None


def _secure_randint(a: int, b: int) -> int:
    random_int = secrets.randbelow(b - a + 1) + a
    return random_int


def _mod_inverse(a: int, m: int) -> int:
    def egcd(a, b):
        if a == 0:
            return b, 0, 1
        else:
            g, y, x = egcd(b % a, a)
            return g, x - (b // a) * y, y

    g, x, y = egcd(a, m)
    if g != 1:
        raise ValueError("Could not calculate inverse: %d and %d" % (a, m))
    else:
        return x % m


def _int_to_bytes(i: int) -> bytes:
    return i.to_bytes(length=(i.bit_length() + 7) // 8, byteorder='big', signed=i < 0)


class SigningKey(ABC):
    @abstractmethod
    def sign(self, data: bytes) -> bytes:
        pass

    @abstractmethod
    def verify(self, signature: bytes, data: bytes) -> bool:
        pass


class P256SigningKey(SigningKey):
    PARAM_p = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
    PARAM_a = 0xffffffff00000001000000000000000000000000fffffffffffffffffffffffc
    PARAM_b = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b
    PARAM_G = (0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296,
               0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5)
    PARAM_n = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551
    PARAM_h = 0x1
    N_MINUS_TWO = PARAM_n - 2
    OID = "1.2.840.10045.3.1.7"

    def __init__(self, private_key: int):
        super().__init__()
        self._private_key = private_key
        self._public_key = self._point_multiply(private_key, self.PARAM_G)

    @classmethod
    def _point_add(cls, p1: Point, p2: Point) -> Optional[Point]:
        if p1 is None:
            return p2
        if p2 is None:
            return p1
        x1, y1 = p1
        x2, y2 = p2
        if x1 == x2 and y1 != y2:
            return None
        if x1 == x2:
            m = (3 * x1 * x1 + cls.PARAM_a) * pow(2 * y1, cls.PARAM_p - 2, cls.PARAM_p)
        else:
            m = (y1 - y2) * pow(x1 - x2, cls.PARAM_p - 2, cls.PARAM_p)
        x3 = (m * m - x1 - x2) % cls.PARAM_p
        y3 = (m * (x1 - x3) - y1) % cls.PARAM_p
        p = (x3, y3)
        return p

    @classmethod
    def _point_multiply(cls, k: int, p: Point) -> Point:
        result = None
        addend = p
        while k:
            if k & 1:
                result = cls._point_add(result, addend)
            addend = cls._point_add(addend, addend)
            k >>= 1
        return result

    def sign(self, data):
        while 1:
            while 1:
                k = _secure_randint(1, self.PARAM_n - 1)
                k_inv = pow(k, self.N_MINUS_TWO, self.PARAM_n)
                r = self._point_multiply(k, self.PARAM_G)[0]
                r %= self.PARAM_n
                if r != 0:
                    break
            hashed = hashlib.sha256(data).digest()
            e = int.from_bytes(hashed, byteorder='big')
            s = self._private_key * r
            s += e
            s *= k_inv
            s %= self.PARAM_n
            if s != 0:
                break
        seq = univ.Sequence()
        seq.setComponentByPosition(0, univ.Integer(r))
        seq.setComponentByPosition(1, univ.Integer(s))
        return encoder.encode(seq)

    def verify(self, signature, data):
        n = self.PARAM_n
        seq, _ = decoder.decode(signature)
        r = int(seq.components[0])
        s = int(seq.components[1])

        if r <= 0 or s <= 0:
            return False

        if r >= n or s >= n:
            return False

        hashed = hashlib.sha256(data).digest()
        e = int.from_bytes(hashed, byteorder='big')
        w = _mod_inverse(s, n)
        if w is None:
            return False

        u1 = e * w
        u1 %= n
        u2 = r * w
        u2 %= n

        p1 = self._point_multiply(u1, self.PARAM_G)
        p2 = self._point_multiply(u2, self._public_key)
        x, y = self._point_add(p1, p2)
        if x == 0 and y == 0:
            return False

        x %= n
        return x == r


class SM2SigningKey(P256SigningKey):
    PARAM_p = 0xfffffffeffffffffffffffffffffffffffffffff00000000ffffffffffffffff
    PARAM_a = 0xfffffffeffffffffffffffffffffffffffffffff00000000fffffffffffffffc
    PARAM_b = 0x28e9fa9e9d9f5e344d5a9e4bcf6509a7f39789f515ab8f92ddbcbd414d940e93
    PARAM_G = (0x32c4ae2c1f1981195f9904466a39c9948fe30bbff2660be1715a4589334c74c7,
               0xbc3736a2f4f6779c59bdcee36b692153d0a9877cc62a474002df32e52139f0a0)
    PARAM_n = 0xfffffffeffffffffffffffffffffffff7203df6b21c6052b53bbf40939d54123
    PARAM_h = 0x01
    OID = "1.2.156.10197.1.301"

    def __init__(self, private_key):
        super().__init__(private_key)
        self._z = self._za(self._public_key)

    @classmethod
    def _za(cls, public_key: Point, uid: bytes=b'1234567812345678') -> bytes:
        """
        密码学哈希算法

        ZA = H256(ENTLA | IDA | a | b | xG | yG | xA | yA)
        """
        array = bytearray()
        uid_len = len(uid)
        if uid_len >= 8192:
            raise ValueError("SM2: uid too large")

        entla = uid_len * 8
        array.append((entla >> 8) & 0xff)
        array.append(entla & 0xff)

        if uid_len > 0:
            array.extend(uid)

        array.extend(_int_to_bytes(cls.PARAM_a))
        array.extend(_int_to_bytes(cls.PARAM_b))
        array.extend(_int_to_bytes(cls.PARAM_G[0]))
        array.extend(_int_to_bytes(cls.PARAM_G[1]))
        array.extend(_int_to_bytes(public_key[0]))
        array.extend(_int_to_bytes(public_key[1]))
        return new_sm3_hash(array).digest()

    def sign(self, data):
        """
        SM2 签名，基于 GB/T 32918.2-2016

        步骤 1: M' = Za || M
        步骤 2: e = Hash(M')
        步骤 3: 在 [1, n-1] 范围内随机选取 k
        步骤 4: P(x,y) = [k]G(x,y)
        步骤 5: r = (e + x1) mod n，若 r = 0 或 r + k = n 则返回步骤 3
        步骤 6: s = ((1 + D)^-1 · (k - r · D)) mod n，若 s = 0 则返回步骤 3
        步骤 7: 将 r 和 s 编码为 ASN.1-DER 格式
        """
        n = self.PARAM_n

        m = self._z + data

        hm = new_sm3_hash(m).digest()
        e = int.from_bytes(hm, byteorder='big')

        for _ in range(100):
            k = _secure_randint(1, n - 1)

            kp = self._point_multiply(k, self.PARAM_G)

            r = (e + kp[0]) % n
            if r == 0 or r + k == n:
                continue

            d_1 = pow(self._private_key + 1, n - 2, n)
            s = (d_1 * (k + r) - r) % n
            if s == 0:
                continue

            seq = univ.Sequence()
            seq.setComponentByPosition(0, univ.Integer(r))
            seq.setComponentByPosition(1, univ.Integer(s))
            return encoder.encode(seq)

        raise SdkException("sm2 sign failed")

    def verify(self, signature, data):
        """
        SM2 验签，基于 GB/T 32918.2-2016

        步骤 1: 断言 r 在 [1, n-1] 范围内
        步骤 2: 断言 s 在 [1, n-1] 范围内
        步骤 3: M' = Za || M
        步骤 4: e = Hash(M')
        步骤 5: t = (r + s) mod n，若 t = 0 则失败
        步骤 6: P(x,y) = [s]G(x,y) + [t]Pub(x,y)
        步骤 7: R = (e + x1) mod n，断言 R = r
        """
        n = self.PARAM_n
        seq, _ = decoder.decode(signature)
        r = int(seq.components[0])
        s = int(seq.components[1])

        if r < 1 or r > n - 1:
            return False

        if s < 1 or s > n - 1:
            return False

        m = self._z + data

        hm = new_sm3_hash(m).digest()
        e = int.from_bytes(hm, byteorder='big')

        t = (r + s) % n
        if t == 0:
            return False

        p = self._point_add(self._point_multiply(s, self.PARAM_G), self._point_multiply(t, self._public_key))

        r_ = (e + p[0]) % n
        return r_ == r
