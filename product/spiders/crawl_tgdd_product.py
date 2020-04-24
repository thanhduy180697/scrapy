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
# urllib.request.urlretrieve(item['link_image'], "image/{}.jpg".format(index))
# index = index + 1
class CrawlerSpider(Spider):
    name = "crawler_product_tgdd"
    
    allowed_domains = ["thegioididong.com"]
    start_urls = [
        "https://www.thegioididong.com/dtdd",
    ]
    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    limit = 10
    count_crawl = 0

    script = """
        function main(splash)
            local url = splash.args.url
            assert(splash:go(url))
            assert(splash:wait(2))
            local element = splash:select('a.viewmore')
            while (element ~= nil)
            do
                assert(element:mouse_click())
                assert(splash:wait(2))
                element = splash:select('a.viewmore')
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

        questions = Selector(response).xpath('//ul[@class="homeproduct  "]/li[@class="item"]')
        questions_feature = Selector(response).xpath('//ul[@class="homeproduct  "]/li[@class="item feature"]')
        
        for question in questions:
            price = question.xpath('a/div[@class="price"]/strong/text()').extract_first()
            if(price is not None):
                item = ProductItem()
                item['product_name'] = question.xpath('a/h3/text()').extract_first()
                item['product_price'] =price.extract_first().replace('\xa0\u20ab','').replace('\u20ab','')
                item['product_link'] = response.urljoin(question.xpath('a/@href').extract_first())
                item['link_image'] = question.xpath('a/img/@src').extract_first()
                item['product_provider'] = 1
                item['date_crawl_product'] = self.timestamp
                if item['link_image'] is None:
                    item['link_image'] = question.xpath('a/img/@data-original').extract_first()
                yield item
            #if(question.xpath('a/label[@class="preorder"]').extract_first() is None):


        for question in questions_feature:
            price = question.xpath('a/div[@class="price"]/strong/text()').extract_first()
            if(price is not None):
                item = ProductItem()
                item['product_name'] = question.xpath('a/h3/text()').extract_first()
                item['product_price'] = question.xpath('a/div[@class="price"]/strong/text()').extract_first().replace('\xa0\u20ab','').replace('\u20ab','')
                item['product_link'] = response.urljoin(question.xpath('a/@href').extract_first())
                item['link_image'] = question.xpath('a/img/@src').extract_first()
                item['product_provider'] = 1
                item['date_crawl_product'] = self.timestamp
                if item['link_image'] is None:
                    item['link_image'] = question.xpath('a/img/@data-original').extract_first()
                yield item

 

#Crawl 157 product
#Honor 9 Lite-3
#157+586=743
#744 + 253 = 997
#157+195+113+165+172+140=