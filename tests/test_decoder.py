# -*- coding: utf-8 -*-
# Created by apple on 2019/11/24.

from io import BytesIO
from collections import OrderedDict
from bencode import BEncodeDecoder

simple_datas = [
    b'de',
    b'l1:ae',
    b'd1:ai10086ee',
]
simple_datas_decode = [
    OrderedDict(),
    ['?'],
    OrderedDict({'a': '?'}),
]
simple_test_decode_datas = zip(simple_datas, simple_datas_decode)


def test_decoder():
    def __object_hook(obj: dict) -> object:
        return OrderedDict(obj)

    def __object_pairs_hook(_obj: object) -> object:
        return '?'

    d = BEncodeDecoder(object_hook=__object_hook, object_pairs_hook=__object_pairs_hook)
    for data, res in simple_test_decode_datas:
        assert res == d.decode(BytesIO(data))
