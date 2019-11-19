# -*- coding: utf-8 -*-
# Created by skytoup on 2019/11/18.

from io import BytesIO
from typing import Optional, Union, BinaryIO


class BEncodeDecodeError(ValueError):
    def __init__(self, msg, pos):
        errmsg = f'{msg}: (char {pos})'
        ValueError.__init__(self, errmsg)
        self.msg = msg
        self.pos = pos

    def __reduce__(self):
        return self.__class__, (self.msg, self.pos)


class BEncode:
    """
    bencode的编码、解码工具
    解码时, dict的key将decode为str(应该不会有key使用非utf-8吧), value不做decode, 保持为bytes


    bencode简介

    数据类型: integer, string(应该是指cstr), dict, list

    数据格式
        - integer
            - i<整数>e
            - eg: 10086 -> b'i10086e'
        - string
            - <字符串长度>:<字符串(cstr)>
            - eg: 'hello world' -> b'11:hello world'
        - list
            - l[数据1][数据2][数据3][…]e
            - eg: [1, 2, 3, '4'] -> b'li1ei2ei3e1:4e'
        - dict
            - d[key1(必须为string)][value1][key2][value2][…]e
            - key需要按字典排序, 且必须为string类型
            - eg: {'a': 1, 'c': 2, 'b': '2'} -> b'd1:ai1e1:b1:21:ci2ee'

    TODO:
        - 类似json库的Encoder和Decoder

    """
    __number_bs = set(b'0 1 2 3 4 5 6 7 8 9'.split())
    __dict_bs = b'd'
    __list_bs = b'l'
    __int_bs = b'i'
    __split_bs = b':'
    __end_bs = b'e'

    @classmethod
    def load(cls, fp: BinaryIO) -> Union[dict, list, int, bytes]:
        """
        加载bencode

        解码错误会抛出BEncodeDecodeError

        :param fp: 二进制可读的buff io
        :return:
        """
        return cls.__read_value(fp)

    @classmethod
    def loads(cls, s: Union[str, bytes]) -> Union[dict, list, int, bytes]:
        """
        加载bencode

        解码错误会抛出BEncodeDecodeError

        :param s: 需要解码的数据
        :return:
        """
        buff = BytesIO(s if isinstance(s, bytes) else s.encode())
        return cls.load(buff)

    @classmethod
    def dump(cls, obj: Union[dict, list, tuple, int, bytes, str], fp: BinaryIO):
        """
        对象编码bencode

        对象编码错误会抛出ValueError或TypeError

        :param obj: 需要编码的对象, 可嵌套, 但是仅支持dict、list、int、bytes、str
        :param fp: 二进制可写的buff io
        :return:
        """
        cls.__write_value(fp, obj)

    @classmethod
    def dumps(cls, obj: Union[dict, list, tuple, int, bytes, str]) -> bytes:
        """
        对象编码bencode

        :param obj: 需要编码的对象, 可嵌套, 但是仅支持dict、list、int、bytes、str
        :return:
        """
        buff = BytesIO()
        cls.dump(obj, buff)
        bs = buff.getvalue()
        buff.close()
        return bs

    @staticmethod
    def __decode_error(msg: str, buff: BinaryIO):
        raise BEncodeDecodeError(msg, buff.tell() - 1)

    @staticmethod
    def __bs_to_int(bs: bytes):
        return ord(bs) - 48  # b'0'

    @classmethod
    def __write_value(cls, buff: BinaryIO, value: Union[dict, list, tuple, int, bytes, str]):
        """
        向buff写入一个value

        :param buff:
        :param value:
        :return:
        """
        # TODO: - 防止对象循环引用, 导致一直循环编码
        if isinstance(value, dict):
            cls.__write_dict(buff, value)
        elif isinstance(value, list) or isinstance(value, tuple):
            cls.__write_list(buff, value)
        elif isinstance(value, int):
            cls.__write_int(buff, value)
        elif isinstance(value, str) or isinstance(value, bytes):
            cls.__write_str(buff, value)
        else:
            raise TypeError(f'Object of type {value.__class__.__name__} is not bencode serializable')

    @classmethod
    def __write_int(cls, buff: BinaryIO, data: int):
        """
        向buff写入一个int

        :param buff:
        :param data:
        :return:
        """
        buff.write(cls.__int_bs)
        buff.write(str(data).encode())
        buff.write(cls.__end_bs)

    @classmethod
    def __write_str(cls, buff: BinaryIO, data: Union[str, bytes]):
        """
        向buff写入一个str

        :param buff:
        :param data:
        :return:
        """
        bs = data if isinstance(data, bytes) else data.encode()
        buff.write(str(len(bs)).encode())
        buff.write(cls.__split_bs)
        buff.write(bs)

    @classmethod
    def __write_list(cls, buff: BinaryIO, data: Union[list, tuple]):
        """
        向buff写入一个list

        :param buff:
        :param data:
        :return:
        """
        buff.write(cls.__list_bs)
        for value in data:
            cls.__write_value(buff, value)
        buff.write(cls.__end_bs)

    @classmethod
    def __write_dict(cls, buff: BinaryIO, data: dict):
        """
        向buff写入一个dict

        :param buff:
        :param data:
        :return:
        """
        buff.write(cls.__dict_bs)
        for k, v in sorted(data.items()):
            if not (isinstance(k, bytes) or isinstance(k, str)):
                raise TypeError(f'keys must be str, bytes, not {k.__class__.__name__}')
            cls.__write_str(buff, k)
            cls.__write_value(buff, v)
        buff.write(cls.__end_bs)

    @classmethod
    def __read_value(cls, buff: BinaryIO, b: bytes = None) -> Union[dict, list, int, bytes]:
        """
        读取一个value

        :param buff:
        :param b: 已经预读取一个bytes
        :return:
        """
        if b is None:
            b = buff.read(1)

        if b == cls.__dict_bs:
            return cls.__read_dict(buff)
        elif b == cls.__list_bs:
            return cls.__read_list(buff)
        elif b == cls.__int_bs:
            return cls.__read_int(buff)
        elif b in cls.__number_bs:
            return cls.__read_bs(buff, b)
        else:
            cls.__decode_error(f'Unknow value type {b}', buff)

    @classmethod
    def __read_dict(cls, buff: BinaryIO) -> dict:
        """
        读取一个dict

        :param buff:
        :return:
        """
        data = {}
        while 1:
            b = buff.read(1)
            if b == cls.__end_bs:
                return data

            key = cls.__read_str(buff, b)
            if key is None:
                cls.__decode_error('Invalid dict key', buff)

            value = cls.__read_value(buff)
            if value is None:
                cls.__decode_error('Invalid dict value', buff)

            data[key] = value

    @classmethod
    def __read_list(cls, buff: BinaryIO) -> list:
        """
        读取一个list

        :param buff:
        :return:
        """
        data = []
        while 1:
            b = buff.read(1)
            if b == cls.__end_bs:
                return data

            value = cls.__read_value(buff, b)
            if value is None:
                cls.__decode_error('Invalid list value', buff)

            data.append(value)

    @classmethod
    def __read_bs(cls, buff: BinaryIO, first_bs: bytes) -> bytes:
        """
        读取一个cstr

        :param buff:
        :param first_bs: 已经预读取一个bytes
        :return:
        """
        data = cls.__just_read_int(buff, cls.__split_bs, first_bs)
        if data is None:
            cls.__decode_error('Invalid str', buff)
        return buff.read(data)

    @classmethod
    def __read_str(cls, buff: BinaryIO, first_bs: bytes) -> str:
        """
        读取一个str

        :param buff:
        :param first_bs: 已经预读取一个bytes
        :return:
        """
        return cls.__read_bs(buff, first_bs).decode()

    @classmethod
    def __read_int(cls, buff: BinaryIO, first_bs: bytes = None) -> int:
        data = cls.__just_read_int(buff, cls.__end_bs, first_bs)
        if data is None:
            cls.__decode_error('Invalid int', buff)
        return data

    @classmethod
    def __just_read_int(cls, buff: BinaryIO, end_bs: bytes, first_bs: bytes = None) -> Optional[int]:
        """
        指定一个结束符号, 读取一个int

        :param buff:
        :param end_bs: 标记读取结束的
        :param first_bs: 已经预读取一个bytes
        :return:
        """
        data = cls.__bs_to_int(first_bs) if first_bs else 0  # b'0'

        while 1:
            b = buff.read(1)
            if b in cls.__number_bs:
                data *= 10
                data += cls.__bs_to_int(b)
            elif b == end_bs:
                return data
            else:
                return None
