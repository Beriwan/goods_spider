# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SkuinfoItem(scrapy.Item):
    # define the fields for your item here like:
    itemId = scrapy.Field()
    skuinfo = scrapy.Field()
    change = scrapy.Field()
    time = scrapy.Field()
    account = scrapy.Field()
    itemprice = scrapy.Field()
    quantity = scrapy.Field()
    content = scrapy.Field()

    pass


class TbGoodsItem(scrapy.Item):
    # define the fields for your item here like:
    itemId = scrapy.Field()
    shopId = scrapy.Field()
    sellerId = scrapy.Field()
    sellerNick = scrapy.Field()
    shopName = scrapy.Field()
    shopVer = scrapy.Field()
    pic = scrapy.Field()
    cid = scrapy.Field()
    shopAge = scrapy.Field()
    goldSeller = scrapy.Field()
    score = scrapy.Field()
    shopimg = scrapy.Field()
    propinfo = scrapy.Field()
    change = scrapy.Field()
    skuinfo = scrapy.Field()
    rcid = scrapy.Field()
    brandId = scrapy.Field()
    quantity = scrapy.Field()
    title = scrapy.Field()
    local = scrapy.Field()
    sellertype = scrapy.Field()
    time = scrapy.Field()
    price = scrapy.Field()
    tb_state = scrapy.Field()
    zb_state = scrapy.Field()

class shopitem(scrapy.Item):
    shopinfo = scrapy.Field()
    itemId = scrapy.Field()
    time = scrapy.Field()