# -*- coding: utf-8 -*-
# Created by apple on 2019/11/24.

from io import BytesIO
from typing import Union, Optional, BinaryIO, Callable

from .define import BEncodeDef


class BEncodeDecodeError(ValueError):
    def __init__(self, msg, pos):
        errmsg = f'{msg}: (char {pos})'
        ValueError.__init__(self, errmsg)
        self.msg = msg
        self.pos = pos

    def __reduce__(self):
        return self.__class__, (self.msg, self.pos)


class BEncodeDecoder:
    def __init__(self, *,
                 object_hook: Optional[Callable[[dict], object]] = None,
                 object_pairs_hook: Optional[Callable[[object], object]] = None,
                 dict_key_use_str: bool = True):
        """
        dencode解码器

        :param object_hook: dict 的 hook
        :param object_pairs_hook: dict value 和 list value 的 hook
        :param dict_key_use_str: dict的key是否使用str, 否则使用bytes
        """
        self.object_hook = object_hook
        self.object_pairs_hook = object_pairs_hook
        self.dict_key_use_str = dict_key_use_str

    def decode(self, buff: [BinaryIO]):
        """
        解码BEncode数据
        :param buff:
        :return:
        """
        return self.__read_value(buff)

    @staticmethod
    def __decode_error(msg: str, buff: BinaryIO):
        raise BEncodeDecodeError(msg, buff.tell() - 1)

    @staticmethod
    def __b_to_int(b: bytes):
        """
        单个bs转int
        :param b:
        :return:
        """
        return ord(b) - 48  # b'0'

    def __read_value(self, buff: BinaryIO, b: bytes = None) -> Union[dict, list, int, bytes]:
        """
        读取一个value

        :param buff:
        :param b: 已经预读取一个bytes
        :return:
        """
        if b is None:
            b = buff.read(1)

        if b == BEncodeDef.dict_bs:
            return self.__read_dict(buff)
        elif b == BEncodeDef.list_bs:
            return self.__read_list(buff)
        elif b == BEncodeDef.int_bs:
            return self.__read_int(buff)
        elif b in BEncodeDef.number_bs:
            return self.__read_bs(buff, b)
        else:
            self.__decode_error(f'Unknow value type {b}', buff)

    def __read_dict(self, buff: BinaryIO) -> dict:
        """
        读取一个dict

        :param buff:
        :return:
        """
        data = {}
        while 1:
            b = buff.read(1)
            if b == BEncodeDef.end_bs:
                return self.object_hook(data) if self.object_hook else data

            key = self.__read_str(buff, b) if self.dict_key_use_str else self.__read_bs(buff, b)
            if key is None:
                self.__decode_error('Invalid dict key', buff)

            value = self.__read_value(buff)
            if value is None:
                self.__decode_error('Invalid dict value', buff)
            elif self.object_pairs_hook:
                value = self.object_pairs_hook(value)

            data[key] = value

    def __read_list(self, buff: BinaryIO) -> list:
        """
        读取一个list

        :param buff:
        :return:
        """
        data = []
        while 1:
            b = buff.read(1)
            if b == BEncodeDef.end_bs:
                return data

            value = self.__read_value(buff, b)
            if value is None:
                self.__decode_error('Invalid list value', buff)
            elif self.object_pairs_hook:
                value = self.object_pairs_hook(value)

            data.append(value)

    def __read_bs(self, buff: BinaryIO, first_bs: bytes) -> bytes:
        """
        读取一个cstr

        :param buff:
        :param first_bs: 已经预读取一个bytes
        :return:
        """
        data = self.__just_read_int(buff, BEncodeDef.split_bs, first_bs)
        if data is None:
            self.__decode_error('Invalid str', buff)
        return buff.read(data)

    def __read_str(self, buff: BinaryIO, first_bs: bytes) -> str:
        """
        读取一个str

        :param buff:
        :param first_bs: 已经预读取一个bytes
        :return:
        """
        return self.__read_bs(buff, first_bs).decode()

    def __read_int(self, buff: BinaryIO, first_bs: bytes = None) -> int:
        data = self.__just_read_int(buff, BEncodeDef.end_bs, first_bs)
        if data is None:
            self.__decode_error('Invalid int', buff)
        return data

    def __just_read_int(self, buff: BinaryIO, end_bs: bytes, first_bs: bytes = None) -> Optional[int]:
        """
        指定一个结束符号, 读取一个int

        :param buff:
        :param end_bs: 标记读取结束的
        :param first_bs: 已经预读取一个bytes
        :return:
        """
        data = self.__b_to_int(first_bs) if first_bs else 0  # b'0'

        while 1:
            b = buff.read(1)
            if b in BEncodeDef.number_bs:
                data *= 10
                data += self.__b_to_int(b)
            elif b == end_bs:
                return data
            else:
                return None
