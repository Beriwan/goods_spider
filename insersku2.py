
import json
import time

from goods_spider.db import Mysql, RedisClient
from goods_spider.settings import SKU_NAME




def get_change(content):
    try:
        return tuple(content['content'])
    except Exception:
        return None


def main():
    mysql = Mysql()
    R = RedisClient(SKU_NAME)
    items = R.r.llen('skuinfo:items')
    print(items)
    for i in range(0, 1):
        item = R.r.blpop('skuinfo:items')
        print(item)
        # print(item[1])
        contents = json.loads(item[1].decode('utf-8'))
        change_set = get_change(contents)
        print(change_set)

if __name__ =='__main__':
    main()