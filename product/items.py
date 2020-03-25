# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ProductItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    product_name=scrapy.Field()
    product_price=scrapy.Field()
    link_image=scrapy.Field()
    product_link=scrapy.Field()
    average_rating=scrapy.Field()
    date_crawl_product=scrapy.Field()

class ReviewItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name_user=scrapy.Field()
    review_user=scrapy.Field()
    name_product=scrapy.Field()
