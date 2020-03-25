from scrapy import Spider
from scrapy.selector import Selector
from ..items import ProductItem
from ..items import ReviewItem
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
    name = "crawler_product"
    
    allowed_domains = ["thegioididong.com"]
    start_urls = [
        "https://www.thegioididong.com/dtdd",
    ]
    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url=url,callback=self.parse, args= {"wait" : 7})


    def parse(self, response):

        questions = Selector(response).xpath('//ul[@class="homeproduct  "]/li[@class="item"]')
        questions_feature = Selector(response).xpath('//ul[@class="homeproduct  "]/li[@class="item feature"]')
        
        for question in questions:
            item = ProductItem()
            item['product_name'] = question.xpath('a/h3/text()').extract_first()
            item['product_price'] = question.xpath('a/div[@class="price"]/strong/text()').extract_first()
            item['product_link'] = question.xpath('a/@href').extract_first()
            item['link_image'] = question.xpath('a/img/@src').extract_first()
            item['date_crawl_product'] = self.timestamp
            if item['link_image'] is None:
                item['link_image'] = question.xpath('a/img/@data-original').extract_first()
            if(question.xpath('a/label[@class="preorder"]').extract_first() is None):
                url = question.xpath('a/@href').extract_first()
                url_item=response.urljoin(url+"/danh-gia")
                yield SplashRequest(url=url_item,callback=self.parse_item, args= {"wait" : 3} , meta = {"item" : item})
            else:
                item['average_rating'] = None
                yield item

        for question in questions_feature:
            item = ProductItem()
            item['product_name'] = question.xpath('a/h3/text()').extract_first()
            item['product_price'] = question.xpath('a/div[@class="price"]/strong/text()').extract_first()
            item['product_link'] = question.xpath('a/@href').extract_first()
            item['link_image'] = question.xpath('a/img/@src').extract_first()
            item['date_crawl_product'] = self.timestamp
            if item['link_image'] is None:
                item['link_image'] = question.xpath('a/img/@data-original').extract_first()
            url = question.xpath('a/@href').extract_first()
            url_item=response.urljoin(url+"/danh-gia")
            yield SplashRequest(url=url_item,callback=self.parse_item, args= {"wait" : 3} , meta = {"item" : item})
            # urllib.request.urlretrieve(item['link_image'], "image/{}.jpg".format(index))
            # index = index + 1
 
    def parse_item(self,response):
        itemProduct = response.meta['item']
        itemProduct['average_rating']= response.xpath('//div[@class="toprt"]/div[@class="crt"]/div[@class="lcrt"]/@data-gpa').extract_first()
        yield itemProduct

    def parse_review(self,response):
        itemProduct = response.meta['item']
        if(itemProduct['average_rating'] is None):
            itemProduct['average_rating']= response.xpath('//div[@class="toprt"]/div[@class="crt"]/div[@class="lcrt"]/@data-gpa').extract_first()
            yield itemProduct
        # now = datetime.now()
        # s2 = now.strftime("%d/%m/%Y, %H:%M:%S")
        # review = ReviewItem()
        # product_name  = response.xpath('//ul[@class="breadcrumb"]/li[4]/a/text()').extract_first()
        # get_reviews = Selector(response).xpath('//ul[@class="ratingLst"]/li[@class="par"]')
        # for get_review in get_reviews:
        #     review['name_user'] = get_review.xpath('div[@class="rh"]/span/text()').extract_first()
        #     review['review_user'] = get_review.xpath('div[@class="rc"]/p/i/text()').extract_first()
            
        #     review['product_name'] = product_name
        #     yield review
