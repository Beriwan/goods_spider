# -*- coding: utf-8 -*-
'''
商品详情爬虫
'''
import json
import re
import time
from datetime import datetime

import requests
import scrapy
from pyquery import PyQuery as pq
from scrapy_redis.spiders import RedisSpider

from goods_spider.items import TbGoodsItem
from goods_spider.settings import *


class DetailSpider(RedisSpider):
    name = 'detail'
    redis_key = DETAIL_NAME
    # allowed_domains = ['www.taobao.com']
    # start_urls = ['https://item.taobao.com/item.htm?id=571513815951']


    def __init__(self, *args, **kwargs):
        # Dynamically define the allowed domains list.
        domain = kwargs.pop('domain', '')
        self.allowed_domains = filter(None, domain.split(','))
        super(DetailSpider, self).__init__(*args, **kwargs)


    def taobao_detail(self, response, item):
        config = re.compile('var g_config = (.*?);', re.S)
        content = config.search(response.text).group(1)
        itemId = re.compile('itemId\s+:\s+\'(\d+)\'')
        title = re.compile('title\s+:\s+\'(.*?)\',')
        status = re.compile('status\s+:\s+(.*?),')
        shopId = re.compile('shopId\s+:\s+\'(\d+)\'')
        shopVer = re.compile('shopVer\s+:\s+(\d+),')
        pic = re.compile('pic\s+:\s+\'(.*?)\'')
        sellerId = re.compile('sellerId\s+:\s+\'(\d+)\'')
        sellerNick = re.compile('sellerNick\s+:\s+\'(.*?)\'')
        shopName = re.compile('shopName\s+:\s+\'(.*?)\',')
        rcid = re.compile('rcid\s+:\s+\'(\d+)\'')
        cid = re.compile('cid\s+:\s+\'(\d+)\'')
        shopAge = re.compile('shopAge\s+:\s+\'(.*?)\'')
        item['itemId'] = itemId.search(content).group(1)
        item['title'] = title.search(content).group(1).encode('latin-1').decode('unicode_escape')
        item['shopId'] = shopId.search(content).group(1)
        item['sellerId'] = sellerId.search(content).group(1)
        item['sellerNick'] = sellerNick.search(content).group(1)
        item['shopName'] = shopName.search(content).group(1).encode('latin-1').decode('unicode_escape')
        item['rcid'] = rcid.search(content).group(1)
        item['shopVer'] = shopVer.search(content).group(1)
        item['pic'] = pic.search(content).group(1)
        item['cid'] = cid.findall(content)[1]
        item['shopAge'] = shopAge.search(content).group(1)
        item['sellertype'] = 'C'
        item['tb_state'] = status.search(content).group(1)

    def tmall_detail(self, content, item, doc):
        info = content['itemDO']
        a = doc('#J_UlThumb li')
        item['sellertype'] = 'B'
        item['title'] = info['title']
        item['itemId'] = info['itemId']
        item['shopId'] = content['rstShopId']
        item['sellerId'] = info['userId']
        # item['sellerNick'] = info['sellerNickName'].encode('latin-1').decode('unicode_escape')
        # item['shopName'] = shopName.search(content).group(1).encode('latin-1').decode('unicode_escape')
        item['rcid'] = info['rootCatId']
        item['quantity'] = info['quantity']
        try:
            item['pic'] = content['propertyPics']['default'][0]
        except Exception:
            item['pic'] = a('img').attr('src')
        item['cid'] = info['categoryId']
        # item['shopAge'] = shopAge.search(content).group(1)
        try:
            item['brandId'] = info['brandId']
        except Exception:
            item['brandId'] = ''

    def get_skuinfo(self, response, item, type='C'):

        url = 'https://detailskip.taobao.com/service/getData/1/p1/item/detail/sib.htm?itemId={id}&modules=dynStock,price,xmpPromotion,originalPrice'
        r1 = requests.get(url.format(id=item['itemId']), headers=DEFAULT_REQUEST_HEADERS)
        if type == 'C':
            skuMap = re.compile('skuMap\s+:\s+({.*})')
            try:
                skus = skuMap.search(response.text).group(1)
                skus = json.loads(skus)
            except Exception:
                skus = None
            data = json.loads(r1.text)['data']
        if type == 'B':
            try:
                skus = response['valItemInfo']['skuMap']
            except Exception:
                skus = None
            data = json.loads(r1.text)['data']
        self.parse_sku(skus, item, data)

    def parse_sku(self, skus, item, data):
        sku_list = []
        totalstock = data['dynStock']['sellableQuantity']
        if skus:
            for sku in skus:
                try:
                    skuId = skus[sku]['skuId']
                    stock = data['dynStock']['sku'][sku]['stock']
                    try:
                        price = data['promotion']['promoData'][sku][0]['price']
                        price1 = data['promotion']['promoData']['def'][0]['price']
                    except Exception:
                        price = data['originalPrice'][sku]['price']
                        price1 = data['originalPrice']['def']['price']
                    skuinfo_set = (item['itemId'], skuId, stock, price, sku, item['time'])
                    sku_list.append(skuinfo_set)
                except Exception:
                    try:
                        price1 = data['promotion']['promoData']['def'][0]['price']
                    except Exception:
                        price1 = data['originalPrice']['def']['price']
            item['price'] = price1
            item['skuinfo'] = sku_list
            changes_list = [item['itemId'], price1, totalstock, item['time']]
            item['change'] = changes_list
        else:
            try:
                price = data['promotion']['promoData']['def'][0]['price']
            except Exception:
                price = data['price']
            item['price'] = price
            changes_list = [item['itemId'], price, totalstock, item['time']]
            item['change'] = changes_list

    def get_prop(self, doc, item):
        prop_list = []
        a = doc('dd .J_TSaleProp')
        for item1 in a.items():
            pidname = item1.attr('data-property')
            b = item1.children('li')
            for item2 in b.items():
                try:
                    pid = re.match('(\d+):(\d+)', item2.attr('data-value')).group(1)
                    vid = re.match('(\d+):(\d+)', item2.attr('data-value')).group(2)
                    vidname = item2.children('a span').text()
                    prop_set = (item['itemId'], pid, pidname, vid, vidname, item['time'])
                    prop_list.append(prop_set)
                except Exception:
                    print('没有prop信息')
        item['propinfo'] = prop_list

    def get_shop(self, response, item):
        shop = re.compile('shop\s+:\s+({.*?})', re.S)
        shopurl = re.compile('url\s+:\s+\'(.*?)\'')
        shopinfo = shop.search(response.text).group(1)
        url = shopurl.search(shopinfo).group(1)
        shop_url = 'https:' + url
        try:
            r2 = requests.get(shop_url, headers=DEFAULT_REQUEST_HEADERS)
            score_list = []
            doc1 = pq(r2.text)
            item['shopimg'] = ''
            scores = doc1('.shop-dynamic-score ul li')
            if scores:
                pass
            else:
                scores = doc1('.shop-rate ul li')
            for score in scores.items():
                score = score.children('em').attr('title')
                score_list.append(score)
            item['score'] = score_list
        except Exception as e:
            print(e)


    def parse(self, response):
        try:
            item = TbGoodsItem()
            item['time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            type = re.search('TShop.Setup\((.*?)\);', response.text, re.S)
            doc = pq(response.text)
            if type != None:
                content = json.loads(type.group(1).strip())
                item['tb_state'] = content['itemDO']['auctionStatus']
                if item['tb_state'] == '0':
                    self.tmall_detail(content, item, doc)
                    self.get_skuinfo(content,item,type='B')
                    self.get_prop(doc, item)
                    # self.tmall_shop(doc, item)
                    yield item
                if item['tb_state'] == '-2':
                    self.tmall_detail(content, item, doc)
                    self.get_skuinfo(content, item, type='B')
                    # self.tmall_shop(doc, item)
                    yield item
            elif doc('.error-notice-hd'):
                print('商品下架不存在')
                with open('xiajia_0612.txt', 'a+') as f:
                    f.write(response.url + '\n')
            else:
                self.taobao_detail(response, item)
                # self.get_shop(response, item)
                if item['tb_state'] == '0':
                    self.get_skuinfo(response, item)
                    self.get_prop(doc, item)
                    yield item
                else:
                    item['price'] = re.search('name="current_price" value= "(.*?)"/>', response.text).group(1)
                    yield item
        except Exception as e:
            with open('error_0612.txt', 'a+') as f:
                f.write(response.url + '\n')
                f.write( 'error: %s \n' %e)
