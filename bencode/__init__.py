# -*- coding: utf-8 -*-
# Created by skytoup on 2019/11/18.

from .encoder import BEncodeEncoder
from .decoder import BEncodeDecoder, BEncodeDecodeError

from io import BytesIO
from typing import Union, BinaryIO

_default_encoder = BEncodeEncoder()


def load(fp: BinaryIO, *, cls=None, object_hook=None, object_pairs_hook=None, dict_key_use_str: bool = True) \
        -> Union[dict, list, int, bytes]:
    """
    加载bencode

    解码错误会抛出BEncodeDecodeError

    :param fp: 二进制可读的buff io
    :param cls:
    :param object_hook:
    :param object_pairs_hook:
    :param dict_key_use_str:
    :return:
    """
    decoder_cls = cls or BEncodeDecoder
    d = decoder_cls(object_hook=object_hook, object_pairs_hook=object_pairs_hook, dict_key_use_str=dict_key_use_str)
    return d.decode(fp)


def loads(s: Union[str, bytes], *, cls=None, object_hook=None, object_pairs_hook=None, dict_key_use_str: bool = True) \
        -> Union[dict, list, int, bytes]:
    """
    加载bencode

    解码错误会抛出BEncodeDecodeError

    :param s: 需要解码的数据
    :param cls:
    :param object_hook:
    :param object_pairs_hook:
    :param dict_key_use_str:
    :return:
    """
    decoder_cls = cls or BEncodeDecoder
    d = decoder_cls(object_hook=object_hook, object_pairs_hook=object_pairs_hook, dict_key_use_str=dict_key_use_str)
    buff = BytesIO(s if isinstance(s, bytes) else s.encode())
    return d.decode(buff)


def dump(obj: Union[dict, list, tuple, int, bytes, str], fp: BinaryIO):
    """
    对象编码bencode

    对象编码错误会抛出ValueError或TypeError

    :param obj: 需要编码的对象, 可嵌套, 但是仅支持dict、list、int、bytes、str
    :param fp: 二进制可写的buff io
    :return:
    """
    _default_encoder.encode(obj, fp)


def dumps(obj: Union[dict, list, tuple, int, bytes, str]) -> bytes:
    """
    对象编码bencode

    :param obj: 需要编码的对象, 可嵌套, 但是仅支持dict、list、int、bytes、str
    :return:
    """
    return _default_encoder.encode(obj)
