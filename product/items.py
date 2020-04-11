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
    product_provider=scrapy.Field()
    date_crawl_product=scrapy.Field()

class ReviewItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    reviewer_name=scrapy.Field()
    review_content=scrapy.Field()
    link_image_review=scrapy.Field()
    rating=scrapy.Field()
    product_name=scrapy.Field()
    product_provider=scrapy.Field()
    date_crawl_product=scrapy.Field()

class RatingItem(scrapy.Item):
    average_rating=scrapy.Field()
    product_name=scrapy.Field()
    product_provider=scrapy.Field()


class SpecificationItem(scrapy.Item):
    display=scrapy.Field()
    operating_system=scrapy.Field()
    front_camera=scrapy.Field()
    rear_camera=scrapy.Field()
    battery=scrapy.Field()
    ram=scrapy.Field()
    cpu=scrapy.Field()
    brand=scrapy.Field()
    storage=scrapy.Field()
    product_name=scrapy.Field()
    product_provider=scrapy.Field()
    date_crawl_product=scrapy.Field()