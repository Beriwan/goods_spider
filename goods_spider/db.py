'''
Mysql、Redis数据库的一些基本配置
'''

import time
import pymysql
import redis
from goods_spider.settings import *

class RedisClient(object):

    def __init__(self, name):
        self.r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
        self.name = name

    def set_url(self, id, url):
        try:
            self.r.lpush(self.name, url.format(id=id))
            print('插入成功:%s' %id)
        except Exception as e:
            print(e)

    def set_two_url(self,id,id2, url):
        try:
            self.r.lpush(self.name, url.format(id=id,id2=id2))
            print('插入成功:%s and %s' %(id ,id2))
        except Exception as e:
            print(e)


class Mysql(object):

    def __init__(self,table_name='source_taobao_live_itemId'):
        self.connect()
        self.table_name = table_name

    def connect(self):
        try:
            self.db = pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER,
                                      password=MYSQL_PASSWORD, db=MYSQL_DB, port=MYSQL_PORT, charset='utf8')
            self.cursor = self.db.cursor()
            self.cursor.execute('SET NAMES utf8;')
            self.cursor.execute('SET CHARACTER SET utf8;')
            self.cursor.execute('SET character_set_connection=utf8;')
        except pymysql.Error as e:
            print('Error:%s' % e)

    def close_db(self):
        try:
            if self.db:
                self.cursor.close()
                self.db.close()
        except pymysql.Error as e:
            print('Error:%s' % e)

    def get_itemId(self):
        sql = 'select itemId from source_taobao_live_itemId where source_taobao_live_itemId.itemId not in (select itemId from source_taobao_live_itemId_drop)'
        sql1 = 'select * from `{table_name}`'.format(table_name=self.table_name)
        cursor = self.db.cursor()
        cursor.execute(sql1)
        data = cursor.fetchall()
        for item in data:
            yield item[0]
        # print(data)
        cursor.close()
        self.close_db()

    def get_shoplist(self,table = 'source_taobao_goods_detail_0622'):
        sql = 'SELECT itemId FROM `{table}` GROUP BY shopId'.format(table=table)
        cursor = self.db.cursor()
        cursor.execute(sql)
        data = cursor.fetchall()
        for item in data:
            yield item[0]
        # print(data)
        cursor.close()
        self.close_db()

    def get_two(self,sql):
        cursor = self.db.cursor()
        cursor.execute(sql)
        data = cursor.fetchall()
        for item in data:
            yield item


    def insert_one(self, sql):
        # try:
        sql = sql
        self.cursor.execute(sql)
        # print(end1-start)
        self.db.commit()

    def insert_sql(self, sql, list):
        try:
            start = time.time()
            sql = sql
            self.cursor.executemany(sql, list)
            end1 = time.time()
            print(end1-start)
            self.db.commit()
            print("插入成功")
        except pymysql.Error as e:
            print(e)

    def get_sql_sentence(self,tableName, item):
        COLstr = ''  # 列的字段
        for key in item.keys():
            COLstr = COLstr + key + ','
        COLstr = COLstr[:-1]
        for _ in item:
            ROWstr = ''  # 行字段
            for key in item.keys():
                try:
                    ROWstr = (ROWstr + '\'%s\'' + ',') % (item[key])
                except Exception:
                    ROWstr = (ROWstr + '\'{content}\'' + ',').format(content=item[key])
            ROWstr = ROWstr[:-1]
        COLstr = "({})".format(COLstr)
        ROWstr = "({})".format(ROWstr)
        return '{} {} VALUES {}'.format(tableName, COLstr, ROWstr)


if __name__ == '__main__':
    url = 'https://detailskip.taobao.com/service/getData/1/p1/item/detail/sib.htm?itemId={id}&modules=dynStock,price,xmpPromotion,originalPrice'
    mysql = Mysql()
    R = RedisClient(SKU_NAME)
    items = mysql.get_itemId()
    for item in items:
        R.set_url(item, url)
