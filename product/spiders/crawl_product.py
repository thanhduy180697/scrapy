from scrapy import Spider
from scrapy.selector import Selector
from ..items import ProductItem
from ..items import ReviewItem
from scrapy.exceptions import NotConfigured
from scrapy_splash import SplashRequest
import urllib.request
from unidecode import unidecode
from datetime import datetime
class CrawlerSpider(Spider):
    name = "crawler_product"
    
    allowed_domains = ["thegioididong.com"]
    start_urls = [
        "https://www.thegioididong.com/dtdd",
    ]
    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url=url,callback=self.parse, args= {"wait" : 7})


    def parse(self, response):
        now = datetime.now()
        s2 = now.strftime("%d/%m/%Y, %H:%M:%S")
        questions = Selector(response).xpath('//ul[@class="homeproduct  "]/li[@class="item"]')
        questions_feature = Selector(response).xpath('//ul[@class="homeproduct  "]/li[@class="item feature"]')
        index = 1
        
        for question in questions:
            if(question.xpath('a/label[@class="preorder"]').extract_first() is None):
                url = question.xpath('a/@href').extract_first();
                url_item=response.urljoin(url)
                yield SplashRequest(url=url_item,callback=self.parse_item, args= {"wait" : 3})
            else:
                item = ProductItem()
                item['product_name'] = question.xpath('a/h3/text()').extract_first()
                item['product_price'] = question.xpath('a/div[@class="price"]/strong/text()').extract_first()
                item['product_link'] = question.xpath('a/@href').extract_first()
                item['link_image'] = question.xpath('a/img/@src').extract_first()
                item['date_crawl_product'] = s2
                if item['link_image'] is None:
                    item['link_image'] = question.xpath('a/img/@data-original').extract_first()
                # urllib.request.urlretrieve(item['link_image'], "image/{}.jpg".format(index))
                # index = index + 1
                yield item

        for question in questions_feature:
            now = datetime.now()
            s2 = now.strftime("%d/%m/%Y, %H:%M:%S")
            item = ProductItem()
            item['product_name'] = question.xpath('a/h3/text()').extract_first()
            item['product_price'] = question.xpath('a/div[@class="price"]/strong/text()').extract_first()
            item['product_link'] = question.xpath('a/@href').extract_first()
            item['link_image'] = question.xpath('a/img/@src').extract_first()
            item['date_crawl_product'] = s2
            if item['link_image'] is None:
                item['link_image'] = question.xpath('a/img/@data-original').extract_first()
            # urllib.request.urlretrieve(item['link_image'], "image/{}.jpg".format(index))
            # index = index + 1

            yield item
 
    def parse_item(self,response):
        now = datetime.now()
        s2 = now.strftime("%d/%m/%Y, %H:%M:%S")
        item = ProductItem()
        item['product_name'] = response.xpath('//div[@class="rowtop"]/h1/text()').extract_first()
        item['product_name'] = unidecode(item['product_name']).replace('Dien thoai ','')

        item['product_price'] = response.xpath('//div[@class="area_price"]/strong/text()').extract_first()
        if(item['product_price'] is None):
            item['product_price'] = response.xpath('//div[@id="wrap_cart"]/strong[@class="pricesell"]/text()').extract_first()
        item['product_link'] = response.url
        item['link_image'] = response.xpath('//aside[@class="picture"]/img/@src').extract_first()
        item['average_rating'] = response.xpath('//div[@id="boxRatingCmt"]/div[@class="toprt"]/div[@class="crt"]/div[@class="lcrt "]/@data-gpa').extract_first()
        item['date_crawl_product'] = s2  
        if(item['average_rating'] is not None):
            yield item
        url_review = response.xpath('//div[@id="boxRatingCmt"]/a/@href').extract_first()
        if(url_review is not None):
            url = response.urljoin(url_review)
            yield SplashRequest(url=url,callback=self.parse_review, args= {"wait" : 3}, meta = {"item" : item})

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
