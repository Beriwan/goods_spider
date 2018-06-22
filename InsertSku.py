'''
将抓取的sku、change信息批量插入Mysql
'''

import json
import time

from goods_spider.db import Mysql, RedisClient
from goods_spider.settings import SKU_NAME


def get_change(content):
    try:
        return content['change']
    except Exception:
        return None


def get_sku(content):
    try:
        if content['skuinfo']:
            return content['skuinfo']
        else:
            return None
    except Exception:
        return None


def main():
    mysql = Mysql()
    R = RedisClient(SKU_NAME)
    list_wdetail = []
    list_prop = []
    list_changes = []
    list_skuinfo = []
    list_shopinfo = []
    list_shopscore = []
    items = R.r.llen('skuinfo:items')
    print(items)
    for i in range(0, items):
        item = R.r.blpop('skuinfo:items')
        # print(item[1])
        contents = json.loads(item[1].decode('utf-8'))
        change_set = get_change(contents)
        list_changes.append(tuple(change_set))
        sku_list = get_sku(contents)
        if sku_list != None:
            for sku in sku_list:
                list_skuinfo.append(tuple(sku))
    sql_change = "insert into source_taobao_goods_change(itemId,itemprice,quantity,deposittime)values(%s,%s,%s,%s)"
    mysql.insert_sql(sql_change, list_changes)
    sql_sku = "insert into source_taobao_goods_skuinfo(itemId,quantity,price,propPath,updatetime)values(%s,%s,%s,%s,%s)"
    mysql.insert_sql(sql_sku, list_skuinfo)
    mysql.close_db()
    #     itemId = contents['itemId']
    #     time = contents['time']
    #     change_set = get_change(itemId, value, time)
    #     list_changes.append(change_set)
    #     sku_list = analysis_shuinfo(data, value, itemId, time)
    #     if sku_list != None:
    #         for sku in sku_list:
    #             list_skuinfo.append(sku)
    # insert_sql(list_wdetail, list_prop, list_changes, list_skuinfo, list_shopinfo, list_shopscore)


if __name__ == '__main__':
    while True:
        main()
        print('暂停60')
        time.sleep(60)
