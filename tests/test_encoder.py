# -*- coding: utf-8 -*-
# Created by apple on 2019/11/24.

from typing import BinaryIO
from bencode import BEncodeEncoder

simple_datas = [
    [1, 2, 3, object()],
    object(),
    {'a': 1, 'b': object},
]
simple_datas_encode = [
    b'li1ei2ei3e?e',
    b'?',
    b'd1:ai1e1:b?e',
]
simple_test_encode_datas = zip(simple_datas, simple_datas_encode)


def test_encoder():
    def __default(buff: BinaryIO, _obj: object):
        buff.write(b'?')

    e = BEncodeEncoder(default=__default)
    for data, res in simple_test_encode_datas:
        assert res == e.encode(data)
