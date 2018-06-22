'''
组成抓取sku信息的URL，并将它插入Redis
'''

from goods_spider.db import RedisClient, Mysql
from goods_spider.settings import SKU_NAME

class Skulist(object):

    def set_list(self):
        url = 'https://detailskip.taobao.com/service/getData/1/p1/item/detail/sib.htm?itemId={id}&modules=dynStock,price,xmpPromotion,originalPrice&id=10067452'
        mysql = Mysql()
        R = RedisClient(SKU_NAME)
        items = mysql.get_itemId()
        for item in items:
            R.set_url(item, url)

if __name__ == '__main__':
    run = Skulist()
    run.set_list()