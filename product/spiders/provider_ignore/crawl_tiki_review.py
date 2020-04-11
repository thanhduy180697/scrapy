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
from scrapy.shell import inspect_response

class CrawlerSpider(Spider):
    name = "crawler_reviews_tiki"
    
    allowed_domains = ["tiki.vn"]
    start_urls = [
        "https://tiki.vn/dien-thoai-smartphone/c1795?src=static_block"
    ]
    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    limit = 10
    count_crawl = 0

    script = """
        function main(splash)
            splash:init_cookies(splash.args.cookies)
            local url = splash.args.url
            assert(splash:go(url))
            assert(splash:wait(20))
            return {
                cookies = splash:get_cookies(),
                html = splash:html()
            }
        end
        """

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url="https://tiki.vn/dien-thoai-samsung-galaxy-note-10-plus-256gb-12gb-hang-chinh-hang-da-kich-hoat-bao-hanh-dien-tu-p29454689.html?src=category-page-1789.1795&2hi=0",callback=self.parse_item,endpoint='render.html', args= {"wait" : 2},meta={
                            "splash": {"endpoint": "execute", "args": {"lua_source": self.script}}})


    def parse(self, response):
        
        products = Selector(response).xpath('//div[@class="product-box-list"]/div[@class="product-item    "]')
        for product in products:
            link = product.xpath('a/@href').extract_first()
            yield SplashRequest(url=link,callback=self.parse_item, args= {"wait" : 10})

        # if(response.xpath('//a[@class="next"]/@href').extract_first() is not None):
        #     url = response.urljoin(response.xpath('//a[@class="next"]/@href').extract_first())

        #     yield SplashRequest(url=url,callback=self.parse, args= {"wait" : 1})
    
    def parse_item(self,response):
        inspect_response(response,self)
        review = ReviewItem()
        
        review['product_name'] = (response.xpath('//h1[@id="product-name"]/span[3]/text()').extract_first()).replace('\u0110i\u1ec7n Tho\u1ea1i ','')
        review['product_name'] = review['product_name'].replace('\u0110i\u1ec7n tho\u1ea1i','').strip()
        
        get_reviews = Selector(response).xpath('//div[@class="review-list"]/div[@class="item"]')

        for get_review in get_reviews:
            if(self.count_crawl < self.limit):
                review['reviewer_name'] = get_review.xpath('div[@class="product-col-1"]/p[@class="name"]/text()').extract_first()
                       
                review['review_content'] = get_review.xpath('div[@class="product-col-2"]/div[@class="infomation"]/div[@class="description js-description"]/p/text()"]/text()').extract_first()
                review['review_content'] = review['review_content'].replace('\n','').strip()
                
                review['rating'] = get_review.xpath('div[@class="product-col-2"]/div[@class="infomation"]/div[@class="rating"]/span[@class="rating-content"]/span/@style').extract()
                review['rating'] = int(review['rating'].replace('width: ','').replace('%;',''))
                
                review['date_crawl_product'] = self.timestamp
                review['product_provider'] = 4

                review['link_image_review'] = ''
                images = get_review.xpath('div[@class="product-col-2"]/div[@class="infomation"]/div[@class="images"]/a').extract_first()
                for image in images:
                    review['link_image_review'] = review['link_image_review'] + image.xpath('@href') + "&&"
                self.count_crawl += 1
                yield review
            else:
                print("Da crawl xong 10 lan")
                self.count_crawl = 0
                return
    



