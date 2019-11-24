# -*- coding: utf-8 -*-
# Created by skytoup on 2019/11/18.

import inspect
from os import path
from bencode import dumps, loads

cur_file = inspect.getfile(inspect.currentframe())
cur_directory = path.dirname(path.abspath(cur_file))
torrent_files = [f'{cur_directory}/torrent/{i + 1}.torrent' for i in range(5)]

simple_encode_datas = [
    b'11:hello world',
    b'li1ei2ei3e1:4e',
    b'd1:ai1e1:b1:21:ci2ee',
    b'i10086e',
]
simple_decode_datas = [
    b'hello world',
    [1, 2, 3, b'4'],
    {'a': 1, 'c': 2, 'b': b'2'},
    10086,
]
simple_datas = zip(simple_decode_datas, simple_encode_datas)

simple_invalid_decode_datas = [
    b'i123',
    b'123e',
    b'li1e',
    b'di1e',
    b'a:0123456789',
]
simple_invalid_encode_datas = [
    1.2,
    [1, 2, 3, 4, 5.0],
    {'a': 1.1},
    {'b': object()},
    object(),
]
circular_ref_a = [1, 2, 3]
circular_ref_b = [3, 2, 1]
circular_ref_c = {'a': 1}
circular_ref_a.append(circular_ref_b)
circular_ref_b.append(circular_ref_a)
circular_ref_c['b'] = circular_ref_c
circular_ref_datas = [
    circular_ref_a,
    circular_ref_b,
    circular_ref_c,
]


def test_simple_encode_decode():
    for d, e in simple_datas:
        encode = dumps(d)
        assert encode == e

        decode = loads(e)
        assert decode == d


def test_torrent():
    for tf in torrent_files:
        with open(tf, 'rb') as f:
            bs = f.read()

            decode_torrent = loads(bs)
            assert decode_torrent is not None

            encode_torrent = dumps(decode_torrent)
            assert encode_torrent is not None

            assert bs == encode_torrent


def test_invalid_encode_data():
    for data in simple_invalid_decode_datas:
        try:
            loads(data)
        except:
            pass
        else:
            assert 0


def test_invalid_decode_data():
    for data in simple_invalid_encode_datas:
        try:
            dumps(data)
        except:
            pass
        else:
            assert 0


def test_decode_circular_ref():
    for data in circular_ref_datas:
        try:
            dumps(data)
        except:
            pass
        else:
            assert 0
