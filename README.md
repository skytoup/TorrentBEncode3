# TorrentBEncode3
> 用于编码、解码torrent文件的bencode格式, 需要Python3.5+


## 安装
`pip3 install torrent-bencode3`

## 测试
1. `git clone https://github.com/skytoup/TorrentBEncode3`
2. `cd TorrentBEncode3`
3. `pip3 install -r requirements-test.txt`
4. `tox`

## 使用
```python3
from bencode import BEncode


s = BEncode.loads(b'11:hello world')  # b'hello world'
BEncode.dumps(s)  # b'11:hello world'

with open('/path/to/torrent', 'rb') as f:
    obj = BEncode.load(f)
    with open('/path/to/save/torrent', 'wb') as wf:
        BEncode.dump(obj, wf)
```
