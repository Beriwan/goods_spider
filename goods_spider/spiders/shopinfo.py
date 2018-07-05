# -*- coding: utf-8 -*-
'''
店铺详情爬虫
'''
import json
import re
import time
from datetime import datetime

import requests
import scrapy
from scrapy_redis.spiders import RedisSpider

from goods_spider.items import shopitem
from goods_spider.settings import DEFAULT_REQUEST_HEADERS, SHOP_NAME


class ShopinfoSpider(RedisSpider):
    name = 'shopinfo'
    redis_key = SHOP_NAME
    # allowed_domains = ['www.taobao.com']
    # start_urls = [
    #     'https://acs.m.taobao.com/h5/mtop.taobao.detail.getdetail/6.0/?data=%7B%22itemNumId%22%3A%22566977632854%22%7D',]

    custom_settings = {
        'DOWNLOAD_DELAY': 1.75,
        'CONCURRENT_REQUESTS': 16,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 16,
        'ITEM_PIPELINES': {'goods_spider.pipelines.ShopSpiderPipeline': 300,},
        # 'DOWNLOADER_MIDDLEWARES': {'goods_spider.middlewares.MyproxisSpiderMidleware': 125, },
    }

    def __init__(self, *args, **kwargs):
        # Dynamically define the allowed domains list.
        domain = kwargs.pop('domain', '')
        self.allowed_domains = filter(None, domain.split(','))
        super(ShopinfoSpider, self).__init__(*args, **kwargs)
        self.count = 1
        self.url = 'https://ext-mdskip.taobao.com/extension/seller_info.htm?callback=jsonpSellerInfo&user_num_id={id}'


    def analysis_shopinfo(self, data, time, maintype):
        try:
            tb_shop = {
                'userId': data['seller']['userId'],
                'shopId': data['seller']['shopId'],
                'shopName': data['seller']['shopName'],
                'shopIcon': data['seller']['shopIcon'],
                'fans': data['seller']['fans'],
                'sellerType': data['seller']['sellerType'],
                'shopType': data['seller']['shopType'],
                'starts': data['seller']['starts'],
                'goodRatePercentage': data['seller']['goodRatePercentage'],
                'sellerNick': data['seller']['sellerNick'],
                'creditLevel': data['seller']['creditLevel'],
                'describe': data['seller']['evaluates'][0]['score'],
                'service': data['seller']['evaluates'][1]['score'],
                'logistics': data['seller']['evaluates'][2]['score'],
                'deposittime': time,
                'maintype': maintype,
            }
            shop_set = (
                tb_shop['userId'], tb_shop['shopId'], tb_shop['shopName'], tb_shop['shopIcon'], tb_shop['fans'],
                tb_shop['sellerType'], tb_shop['shopType'], tb_shop['starts'], tb_shop['goodRatePercentage'],
                tb_shop['sellerNick'], tb_shop['creditLevel'], tb_shop['describe'], tb_shop['service'],
                tb_shop['logistics'], tb_shop['deposittime'], tb_shop['maintype'])
            return shop_set
        except Exception:
            return None, None

    def parse(self, response):
        print(str(self.count) + '===============================================')
        item = shopitem()
        item['time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        content = json.loads(response.text)
        ret = content.get('ret')
        re_drop = re.compile(r'redirectUrl')
        re_id = re.compile(r'itemNumId%22%3A%22(\d+)')
        # item_detail = tb_wetail()
        if re.match(r'FAIL_SYS_USER_VALIDATE:', ret[0]):
            self.r.lpush('urls:test1', response.url)
            print('访问太频繁，重新访问')
            time.sleep(100)
        elif re_drop.search(response.text):
            item['itemId'] = re_id.search(response.url).group(1)
            print('商品过期不存在')
            print(item['itemId'])
            time.sleep(1)
            # yield item
        else:
            item['itemId'] = re_id.search(response.url).group(1)
            data = content['data']
            userid = content['data']['seller']['userId']
            response = requests.get(self.url.format(id=userid), headers=DEFAULT_REQUEST_HEADERS)
            try:
                maintype = re.search('\(所属行业：(.*?)\)', response.text).group(1)
            except Exception:
                maintype = None
            shop_set = self.analysis_shopinfo(data, item['time'], maintype)
            if shop_set != None:
                item['shopinfo'] = shop_set
            yield item
        self.count += 1
