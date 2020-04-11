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
from scrapy.shell import inspect_response

class CrawlerSpider(Spider):
    name = "crawler_product_dttm"
    
    allowed_domains = ["didongthongminh.vn"]
    start_urls = [
        "https://didongthongminh.vn/dien-thoai-chinh-hang"
    ]
    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    limit = 10
    count_crawl = 0
    index=1
    page = 0
    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url=url,callback=self.parse, args= {"wait" : 3})


    def parse(self, response):
        # C\u0169
        products = Selector(response).xpath('//ul[@class="products columns-5"]/li')
        for product in products:          
            price_product = product.xpath('a/span[@class="price"]/span[@class="woocommerce-Price-amount amount"]/text()').extract_first()
            name_product = product.xpath('a/span[@class="dst_hproduct_title"]/span[@class="dst_primtitle"]/text()').extract_first()
            if(price_product is not None and len(price_product) > 2 and name_product.find('C\u0169') < 0):
                item = ProductItem()
                item['product_name'] = name_product
                item['product_price']= price_product.replace(',','.')
                item['product_link'] = product.xpath('a/@href').extract_first()
                item['link_image'] = product.xpath('a/div[@class="dst_lprdc"]/img/@data-original').extract_first()
                
                item['product_provider'] = 4
                item['date_crawl_product'] = self.timestamp
                yield item
                rating = RatingItem()
                rating['product_name'] = item['product_name']
                rating['product_provider'] = 4
                rating['average_rating'] = product.xpath('a/div[@class="star-rating"]/span/strong/text()').extract_first()
                yield rating
                
        display_button = response.xpath('//div[@class="lmp_load_more_button br_lmp_button_settings"]/@style').extract_first()

        if(display_button.find("block") > 0):
            url_next= response.xpath('//div[@class="lmp_load_more_button br_lmp_button_settings"]/a/@href').extract_first()
            yield SplashRequest(url=url_next,callback=self.parse, args= {"wait" : 2})
    
    
    

       



