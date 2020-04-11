from scrapy import Spider
from scrapy.selector import Selector
from ..items import ProductItem
from ..items import RatingItem
from scrapy.exceptions import NotConfigured
from scrapy_splash import SplashRequest
import urllib.request
from unidecode import unidecode
from urllib.parse import urljoin
import datetime
import time

class CrawlerSpider(Spider):
    name = "crawler_product_tiki"
    
    allowed_domains = ["tiki.vn"]
    start_urls = [
        "https://tiki.vn/dien-thoai-smartphone/c1795?src=static_block"
    ]
    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    limit = 10
    count_crawl = 0

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url=url,callback=self.parse, args= {"wait" : 3})


    def parse(self, response):
        
        products = Selector(response).xpath('//div[@class="product-box-list"]/div[@class="product-item    "]')
        for product in products:
            item = ProductItem()
            item['product_name'] = (product.xpath('a/@title').extract_first()).replace('\u0110i\u1ec7n Tho\u1ea1i ','')
            item['product_name'] = item['product_name'].replace('\u0110i\u1ec7n tho\u1ea1i','').strip()
            item['product_name'] = item['product_name'][:item['product_name'].find(' - ')]
            
            item['product_price'] = product.xpath('a/div[@class="content "]/p[@class="price-sale"]/span[@class="final-price"]/text()').extract_first()
            item['product_price'] = item['product_price'].strip().replace('\u0111','')
            
            item['product_link'] = product.xpath('a/@href').extract_first()
            item['link_image'] = product.xpath('a/div[@class="content "]/span[@class="image"]/img[@class="product-image img-responsive"]/@src').extract_first()
            item['product_provider'] = 4
            item['date_crawl_product'] = self.timestamp

            yield item

            if(response.xpath('//a[@class="next"]/@href').extract_first() is not None):
                url = response.urljoin(response.xpath('//a[@class="next"]/@href').extract_first())

                yield SplashRequest(url=url,callback=self.parse, args= {"wait" : 1})

    


