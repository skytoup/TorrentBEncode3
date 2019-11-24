# -*- coding: utf-8 -*-
# Created by apple on 2019/11/24.


class BEncodeDef:
    number_bs = set(b'0 1 2 3 4 5 6 7 8 9'.split())
    dict_bs = b'd'
    list_bs = b'l'
    int_bs = b'i'
    split_bs = b':'
    end_bs = b'e'
