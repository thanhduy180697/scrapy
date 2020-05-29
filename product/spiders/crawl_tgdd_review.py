from scrapy import Spider
from scrapy.selector import Selector
from ..items import ReviewItem
from scrapy.exceptions import NotConfigured
from scrapy_splash import SplashRequest
import urllib.request
from unidecode import unidecode
from urllib.parse import urljoin
import datetime
import time

class CrawlerSpider(Spider):
    name = "crawler_reviews_tgdd"
    
    allowed_domains = ["thegioididong.com"]
    start_urls = [
        "https://www.thegioididong.com/dtdd",
    ]
    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    limit = 50
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
            if(question.xpath('a/label[@class="preorder"]').extract_first() is None):
                url = question.xpath('a/@href').extract_first()
                url_item=response.urljoin(url+"/danh-gia")
                yield SplashRequest(url=url_item,callback=self.parse_item)

        for question in questions_feature:
            url = question.xpath('a/@href').extract_first()
            url_item=response.urljoin(url+"/danh-gia")
            yield SplashRequest(url=url_item,callback=self.parse_item)

 
    def parse_item(self,response):
        review = ReviewItem()
        review['product_name']  = response.xpath('//ul[@class="breadcrumb"]/li[4]/a/text()').extract_first()
        get_reviews = Selector(response).xpath('//ul[@class="ratingLst"]/li[@class="par"]')
        for get_review in get_reviews:
            if(self.count_crawl < self.limit):
                review['reviewer_name'] = get_review.xpath('div[@class="rh"]/span/text()').extract_first()
                review['review_content'] = get_review.xpath('div[@class="rc"]/p/i/text()').extract_first().replace('\n','').strip()
                review['rating'] = len(get_review.xpath('div[@class="rc"]/p/span/i[@class="iconcom-txtstar"]'))
                review['date_crawl_product'] = self.timestamp
                review['product_provider'] = 1
                if(review['rating'] > 5):
                    review['rating'] = review['rating'] / 2
                review_images = get_review.xpath('div[@class="rc"]/div[@class="rat"]/img/@data-original').extract()
                review['link_image_review'] = ""
                if(not review_images):
                    for review_image in review_images:
                        review['link_image_review'] = review['link_image_review'] + review_image + "&&"               
                else:
                    review['link_image_review'] = None
                self.count_crawl += 1
                yield review
            else:
                print("Da crawl xong 50 lan")
                self.count_crawl = 0
                return
         #Update rating product


#3600