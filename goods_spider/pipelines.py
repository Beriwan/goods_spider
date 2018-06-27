# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from goods_spider.db import Mysql
from goods_spider.items import *


class ShopSpiderPipeline(object):
    def process_item(self, item, Spider):
        if isinstance(item, shopitem):
            list = []
            mysql = Mysql()
            print(item['shopinfo'])
            list.append(item['shopinfo'])
            sql_detail = "replace into source_taobao_goods_shopinfo_0625(userId,shopId,shopName,shopIcon,fans,sellerType,shopType,shopage,goodRatePercentage,sellerNick,creditLevel,describe1,service,logistics,deposittime,maintype)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            mysql.insert_sql(sql_detail, list)
            mysql.close_db()
            return item


class SkuSpiderPipeline(object):

    def open_spider(self, Spider):
        self.mysql = Mysql()

    def close_spider(self, Spider):
        self.mysql.close_db()

    def process_item(self, item, Spider):
        if isinstance(item, SkuinfoItem):
            sql_detail = "insert into source_taobao_goods_change_0622_{id}(itemId,itemprice,quantity,deposittime)values('{itemId}','{itemprice}','{quantity}','{deposittime}')".format(
                id=item['account'], itemId=item['itemId'], itemprice=item['itemprice'], quantity=item['quantity'], deposittime=item['time'], )
            self.mysql.insert_one(sql_detail)
            return item
