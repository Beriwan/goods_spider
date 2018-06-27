from goods_spider.db import Mysql, RedisClient
from goods_spider.settings import SHOP_NAME


class ShopList(object):

    def setlist(self):
        url = 'https://acs.m.taobao.com/h5/mtop.taobao.detail.getdetail/6.0/?data=%7B%22itemNumId%22%3A%22{id}%22%7D'
        mysql = Mysql()
        R = RedisClient(SHOP_NAME)
        items = mysql.get_shoplist('source_taobao_goods_detail_0622')
        for item in items:
            R.set_url(item, url)




if __name__ == '__main__':
    run = ShopList()
    run.setlist()