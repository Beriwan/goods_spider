'''
将商品详情表插入MySql
'''
import json
import time
from goods_spider.db import Mysql, RedisClient
from goods_spider.settings import DETAIL_NAME


class DetailInsert(object):

    def get_detail(self, content):
        itemId = content['itemId']
        shopId = content['shopId']
        title = content['title']
        pic = content['pic']
        try:
            price = content['price']
        except Exception:
            price = ''
        tb_state = content['tb_state']
        rcid = content['rcid']
        cid = content['cid']
        try:
            brandId = content['brandId']
        except Exception:
            brandId = ''
        time = content['time']
        sellertype = content['sellertype']
        sellerid = content['sellerId']
        detail_set = (itemId, shopId, sellerid, title, pic, price, tb_state, rcid, cid, time, sellertype)
        return detail_set


    def get_change(self, content):
        try:
            return content['change']
        except Exception:
            return None


    def get_prop(self, content):
        try:
            if content['propinfo'] != '':
                return content['propinfo']
            else:
                return None
        except Exception:
            return None


    def get_sku(self, content):
        try:
            if content['skuinfo']:
                return content['skuinfo']
            else:
                return None
        except Exception:
            return None


    def insertsql(self):
        mysql = Mysql()
        R = RedisClient(DETAIL_NAME)
        list_detail = []
        list_prop = []
        list_changes = []
        list_skuinfo = []
        list_shopinfo = []
        list_shopscore = []
        items = R.r.llen('detail:items')
        print(items)
        for i in range(0, items):
            item = R.r.blpop('detail:items',timeout=5)
            contents = json.loads(item[1])
            list_detail.append(self.get_detail(contents))
            changeinfo = self.get_change(contents)
            if changeinfo != None:
                list_changes.append(tuple(changeinfo))
            propinfo = self.get_prop(contents)
            if propinfo != None:
                for prop in propinfo:
                    list_prop.append(tuple(prop))
            sku_list = self.get_sku(contents)
            if sku_list != None:
                for sku in sku_list:
                    list_skuinfo.append(tuple(sku))
            # list_shopinfo.append(get_shop(contents))
        sql_detail = "replace into source_taobao_goods_detail_0622(itemId,shopId,sellerId,title,headimg,itemprice,tb_state,rootCategoryId,categoryId,deposittime,shopType)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        mysql.insert_sql(sql_detail, list_detail)
        # sql_prop = "replace into source_taobao_goods_prop_0621(itemId,pid,pidname,vid,vidname,deposittime)values(%s,%s,%s,%s,%s,%s)"
        # mysql.insert_sql(sql_prop, list_prop)
        sql_change = "insert into source_taobao_goods_change_0614(itemId,itemprice,quantity,deposittime)values(%s,%s,%s,%s)"
        mysql.insert_sql(sql_change, list_changes)
        # sql_sku = "insert into source_taobao_goods_skuinfo(itemId,skuId,quantity,price,propPath,updatetime)values(%s,%s,%s,%s,%s,%s)"
        # mysql.insert_sql(sql_sku, list_skuinfo)
        mysql.close_db()

def main():
    run = DetailInsert()
    start = time.time()
    run.insertsql()
    end = time.time()
    print(end - start)

if __name__ == '__main__':
    while True:
        main()
        print('3')
        time.sleep(3)