from scrapy import Spider
from scrapy.selector import Selector
from ..items import ProductItem
from scrapy.exceptions import NotConfigured
from scrapy_splash import SplashRequest
import urllib.request
from unidecode import unidecode
from urllib.parse import urljoin
import datetime
import time
from scrapy.shell import inspect_response

class CrawlerSpider(Spider):
    name = "crawler_product_cellphoneS"
    
    allowed_domains = ["cellphones.com.vn"]
    start_urls = [
        "https://cellphones.com.vn/mobile.html"
    ]
    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    limit = 10
    count_crawl = 0
    index= 1
    page = 0

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url=url,callback=self.parse, args= {"wait" : 3})


    def parse(self, response):
        
        products = Selector(response).xpath('//div[@class="products-container"]/ul[@class="cols cols-5"]/li')
        for product in products:
            price = product.xpath('div[@class="lt-product-group-info"]/div[@class="price-box"]/p[@class="special-price"]/span/text()').extract_first()
            if(price is None):
                price = product.xpath('div[@class="lt-product-group-info"]/div[@class="price-box"]/span[@class="regular-price"]/span/text()').extract_first()
            price=price.replace('\xa0\u20ab','')

            if (price != "\u0110\u0103ng k\xfd nh\u1eadn tin"):
                item = ProductItem()
                item['product_price'] = price    
                item['product_name'] = product.xpath('div[@class="lt-product-group-info"]/a/h3/text()').extract_first().replace('\t','').replace(' Chính h\xe3ng','').replace('\u0110i\u1ec7n Tho\u1ea1i ','').replace(' chính h\xe3ng','')
                item['product_link'] = product.xpath('div[@class="lt-product-group-info"]/a/@href').extract_first()
                item['link_image'] = product.xpath('div[@class="lt-product-group-image"]/a/img[1]/@src').extract_first()
                item['product_provider'] = 3
                item['date_crawl_product'] = self.timestamp
                yield item

        if(self.index==1):
            self.page=int(response.xpath('//div[@class="pages"]/ul[@class="pagination"][1]/li[6]/a/text()').extract_first())
            self.index= self.index + 1
            for i in range(self.page-1):
                url_page = "https://cellphones.com.vn/mobile.html?p={}".format(i+2)
                yield SplashRequest(url=url_page,callback=self.parse, args= {"wait" : 1})
    
    #crawl 205 dien thoai
    
    #172
#173
       



