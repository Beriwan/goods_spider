'''
组成抓取商品详情的URL，并插入到Redis队列
'''

from goods_spider.db import *

class DetailList(object):

    def setlist(self):
        url = 'https://item.taobao.com/item.htm?id={id}'
        mysql = Mysql()
        R = RedisClient(DETAIL_NAME)
        items = mysql.get_itemId()
        for item in items:
            R.set_url(item, url)




if __name__ == '__main__':
    run = DetailList()
    run.setlist()
