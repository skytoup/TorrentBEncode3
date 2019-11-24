# -*- coding: utf-8 -*-
# Created by apple on 2019/11/24.

from io import BytesIO
from typing import Union, BinaryIO, Optional, Callable

from .define import BEncodeDef


class BEncodeEncoder:
    def __init__(self, *, default: Optional[Callable[[BinaryIO, object], None]] = None):
        """
        bencode编码器

        :param default: 可自定义该方法实现自定义对象编码
        """
        if default is not None:
            self.default = default

    def default(self, buff: BinaryIO, obj: object):
        """
        读取不是str, bytes, int, list, tuple, dict时调用, 默认抛出异常
        可自定义该方法实现自定义对象编码

        :param buff:
        :param obj:
        :return:
        """
        raise TypeError(f'Object of type {obj.__class__.__name__} is not bencode serializable')

    def encode(self, obj: Union[dict, list, tuple, int, bytes, str], buff: BinaryIO = None) -> Optional[bytes]:
        """
        把对象bencode编码

        :param obj:
        :param buff:
        :return: buff为None时, 返回bytes, 否则不返回, 数据写入传入buff
        """
        has_init_buff = buff is not None
        if not has_init_buff:
            buff = BytesIO()

        self.__write_value(buff, obj)

        if not has_init_buff:
            bs = buff.getvalue()
            buff.close()
            return bs

    def __write_value(self, buff: BinaryIO, value: Union[dict, list, tuple, int, bytes, str],
                      makers: Optional[dict] = None):
        """
        向buff写入一个value

        :param buff:
        :param value:
        :return:
        """
        if isinstance(value, dict):
            self.__write_dict(buff, value, makers)
        elif isinstance(value, list) or isinstance(value, tuple):
            self.__write_list(buff, value, makers)
        elif isinstance(value, int):
            self.__write_int(buff, value)
        elif isinstance(value, str) or isinstance(value, bytes):
            self.__write_str(buff, value)
        else:
            self.default(buff, value)

    @staticmethod
    def __write_int(buff: BinaryIO, data: int):
        """
        向buff写入一个int

        :param buff:
        :param data:
        :return:
        """
        buff.write(BEncodeDef.int_bs)
        buff.write(str(data).encode())
        buff.write(BEncodeDef.end_bs)

    @staticmethod
    def __write_str(buff: BinaryIO, data: Union[str, bytes]):
        """
        向buff写入一个str

        :param buff:
        :param data:
        :return:
        """
        bs = data if isinstance(data, bytes) else data.encode()
        buff.write(str(len(bs)).encode())
        buff.write(BEncodeDef.split_bs)
        buff.write(bs)

    def __write_list(self, buff: BinaryIO, data: Union[list, tuple], makers: Optional[dict]):
        """
        向buff写入一个list

        :param buff:
        :param data:
        :return:
        """
        if makers is None:
            makers = {}

        maker_id = id(data)
        if maker_id in makers:
            raise ValueError('Circular reference detected')
        makers[maker_id] = data

        buff.write(BEncodeDef.list_bs)
        for value in data:
            self.__write_value(buff, value, makers)

        buff.write(BEncodeDef.end_bs)
        del makers[maker_id]

    def __write_dict(self, buff: BinaryIO, data: dict, makers: Optional[dict]):
        """
        向buff写入一个dict

        :param buff:
        :param data:
        :return:
        """
        if makers is None:
            makers = {}

        maker_id = id(data)
        if maker_id in makers:
            raise ValueError('Circular reference detected')
        makers[maker_id] = data

        buff.write(BEncodeDef.dict_bs)
        for k, v in sorted(data.items()):
            if not (isinstance(k, bytes) or isinstance(k, str)):
                raise TypeError(f'keys must be str, bytes, not {k.__class__.__name__}')

            self.__write_str(buff, k)
            self.__write_value(buff, v, makers)

        buff.write(BEncodeDef.end_bs)
        del makers[maker_id]
