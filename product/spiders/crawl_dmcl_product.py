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
    name = "crawler_product_dienmaycholon"
    
    allowed_domains = ["dienmaycholon.vn"]
    start_urls = [
        "https://dienmaycholon.vn/dien-thoai-di-dong"
    ]
    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    limit = 10
    count_crawl = 0
    index=1
    page = 0

    script = """
        function main(splash)
            local url = splash.args.url
            assert(splash:go(url))
            assert(splash:wait(2))
            local element = splash:select('div.load_more')
            while (element ~= nil)
            do
                local link=splash:select('div.load_more > a')
                assert(link:mouse_click())
                assert(splash:wait(2))
                element = splash:select('div.load_more')
            end

            return {
                html = splash:html(),
                url = splash:url(),
            }
        end
        """

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url=url,callback=self.parse, args= {"wait" : 3},meta={
                            "splash": {"endpoint": "execute", "args": {"lua_source": self.script}}})


    def parse(self, response):
        #inspect_response(response,self)

        products = Selector(response).xpath('//ul[@class="list_productcate"]/li')
        for product in products:
            item = ProductItem()
            item['product_name'] = product.xpath('div[@class="item_product"]/div[@class="pro_infomation"]/a/@title').extract_first()
            item['product_name'] = item['product_name'].replace('Di \u0110\u1ed9ng ','').replace('B\u1ed9 S\u1ea3n Ph\u1ea9m ','')
            
            item['product_price']= product.xpath('div[@class="item_product"]/div[@class="pro_infomation"]/div[@class="pro_description"]/strong[@class="price_sale line_throught"]/text()').extract_first()
            if (item['product_price'] is not None):
                item['product_price'] = item['product_price'].strip()
            item['product_link'] = response.urljoin(product.xpath('div[@class="item_product"]/div[@class="pro_infomation"]/a/@href').extract_first())
            item['link_image'] = product.xpath('div[@class="item_product"]/div[@class="pro_infomation"]/div[@class="pro_img"]/a/img/@data-src').extract_first()
            
            item['product_provider'] = 6
            item['date_crawl_product'] = self.timestamp
            yield item
           
#113

       



