
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
    list_changes = []
    R = RedisClient(SKU_NAME)
    items = R.r.llen('skuinfo:items')
    print(items)
    for i in range(0, items):
        item = R.r.blpop('skuinfo:items')
        # print(item[1])
        contents = json.loads(item[1].decode('utf-8'))
        change_set = get_change(contents)
        # print(change_set)
        list_changes.append(tuple(change_set))
    sql_change = "insert into source_taobao_goods_quantity(accountId,itemId,itemprice,quantity,deposittime)values(%s,%s,%s,%s,%s)"
    mysql.insert_sql(sql_change, list_changes)
    mysql.close_db()

if __name__ =='__main__':
    while True:
        main()
        print('暂停60')
        time.sleep(60)