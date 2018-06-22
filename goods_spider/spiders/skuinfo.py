# -*- coding: utf-8 -*-
'''
sku库存价格、商品总库存价格爬虫
'''
import json
import re
from datetime import datetime
import scrapy
from scrapy_redis.spiders import RedisSpider

from goods_spider.items import SkuinfoItem
from goods_spider.settings import SKU_NAME


class SkuinfoSpider(RedisSpider):
    name = 'skuinfo'
    redis_key = SKU_NAME
    # allowed_domains = ['www.taobao.com']
    # start_urls = ['https://detailskip.taobao.com/service/getData/1/p1/item/detail/sib.htm?itemId=557538246682&modules=dynStock,price,xmpPromotion,originalPrice']

    # custom_settings = {
    #     'EXTENSIONS': {'goods_spider.extensions.RedisSpiderSmartIdleClosedExensions': 500,},
    # }

    custom_settings = {
        'CONCURRENT_REQUESTS': 3000,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 100000,
        # 'LOG_LEVEL' : 'INFO'
        # 'ITEM_PIPELINES': {'goods_spider.pipelines.SkuSpiderPipeline': 300, },
        # 'ITEM_PIPELINES': {'goods_spider.pipelines.ShopSpiderPipeline': 300, },
        # 'DOWNLOADER_MIDDLEWARES': {'goods_spider.middlewares.MyproxisSpiderMidleware': 125, },
    }

    def __init__(self, *args, **kwargs):
        # Dynamically define the allowed domains list.
        domain = kwargs.pop('domain', '')
        self.allowed_domains = filter(None, domain.split(','))
        super(SkuinfoSpider, self).__init__(*args, **kwargs)

    # def parse(self, response):
    #     sku_list = []
    #     item = SkuinfoItem()
    #     item['account'] = re.search('id=(\d+)',response.url).group(1)
    #     item['time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #     item['itemId'] = re.search('itemId=(\d+)&',response.url).group(1)
    #     try:
    #         data = json.loads(response.text)['data']
    #     except Exception:
    #         return
    #     totalstock = data['dynStock']['sellableQuantity']
    #     try:
    #         skus = data['dynStock']['sku']
    #         for sku in skus:
    #             stock = data['dynStock']['sku'][sku]['stock']
    #             try:
    #                 price = data['promotion']['promoData'][sku][0]['price']
    #                 price1 = data['promotion']['promoData']['def'][0]['price']
    #             except Exception:
    #                 price = data['originalPrice'][sku]['price']
    #                 price1 = data['originalPrice']['def']['price']
    #             skuinfo_set = (item['itemId'], stock, price, sku, item['time'])
    #             sku_list.append(skuinfo_set)
    #         item['skuinfo'] = sku_list
    #         changes_set = (item['itemId'], price1, totalstock, item['time'])
    #         item['change'] = changes_set
    #     except Exception:
    #         try:
    #             price = data['promotion']['promoData']['def'][0]['price']
    #         except Exception:
    #             price = data['price']
    #         changes_set = (item['itemId'], price, totalstock, item['time'])
    #         item['change'] = changes_set
    #     yield item


    def parse(self, response):
        item = SkuinfoItem()
        item['account'] = re.search('id=(\d+)', response.url).group(1)
        item['time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        item['itemId'] = re.search('itemId=(\d+)&', response.url).group(1)
        try:
            data = json.loads(response.text)['data']
        except Exception:
            print('无信息')
            return
        item['quantity'] = data['dynStock']['sellableQuantity']
        try:
            item['itemprice'] = data['promotion']['promoData']['def'][0]['price']
        except Exception:
            item['itemprice'] = data['price']
        yield item