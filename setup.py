# -*- coding: utf-8 -*-
# Created by apple on 2019/11/18.


from setuptools import setup
from os import path

DIR = path.dirname(path.abspath(__file__))

with open(path.join(DIR, 'README.md')) as f:
    README = f.read()

setup_kwargs = {
    'name': 'torrent-bencode3',
    'version': '0.1.1',
    "license": "MIT",
    'author': 'skytoup',
    'author_email': 'skytoupone1@gmail.com',
    'packages': ['bencode'],
    'platforms': 'any',
    'python_requires': '>=3.5',
    'description': 'torrent文件的编码、解码',
    'long_description': README,
    'long_description_content_type': 'text/markdown',
    'url': 'http://github.com/skytoup/torrent-bencode3',
    'tests_require': [
        'pytest==5.2.4',
        'tox==3.14.1',
    ],
    'keywords': ['torrent', 'bencode', 'encode', 'decode'],
}

setup(**setup_kwargs)
