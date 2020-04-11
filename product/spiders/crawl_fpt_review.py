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
    name = "crawler_reviews_fpt"
    
    allowed_domains = ["fptshop.com.vn"]
    start_urls = [
        "https://fptshop.com.vn/dien-thoai?sort=gia-cao-den-thap&trang=1"
    ]
    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    limit = 40
    count_crawl = 0
    index = 1
    last_page = 0
    
    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url=url,callback=self.parse, args= {"wait" : 3})


    def parse(self, response):
        
        questions = Selector(response).xpath('//div[@class="fs-carow clearfix fs-row4phone viewgrid"]/div[@class="fs-lpil"]')
        for question in questions:
            price = question.xpath('div[@class="fs-lpil-if"]/div[@class="fs-lpilname"]/div[@class="fs-lpil-price"]/p/text()').extract_first()
            product_name = question.xpath('a[@class="fs-lpil-img"]/@title').extract_first()
            if(price is not None and product_name.find('\u0110\u1ed3ng h\u1ed3') < 0 and product_name.find('V\xd2NG') < 0 and product_name.find('Vòng') < 0):
                url_product = question.xpath('div[@class="fs-lpil-if"]/div[@class="fs-lpilname"]/h3[@class="fs-lpil-name"]/a/@href').extract_first()
                url_item=response.urljoin(url_product)
                yield SplashRequest(url=url_item,callback=self.parse_item,meta={
                                "splash": {"endpoint": "execute", "args": {"lua_source": self.script}}, "product_name" : product_name})
        if(self.index==1):
            self.last_page=int(response.xpath('//div[@class="f-cmtpaging"]/a[2]/@data-page').extract_first())
            self.index= self.index + 1           
            for i in range(2,self.last_page+1):
                url_page = "https://fptshop.com.vn/dien-thoai?sort=gia-cao-den-thap&trang={}".format(i)
                yield SplashRequest(url=url_page,callback=self.parse, args= {"wait" : 1})
    
    script = """
        function main(splash)
            local url = splash.args.url
            assert(splash:go(url))
            local id=splash:select('strong#totalrateres').text()
            id = tonumber(id)
            while(id > 0)
            do
                local element = splash:select('strong#totalrateres')
                assert(element:mouse_click())
                assert(splash:wait(2))
                id=tonumber(splash:select('strong#totalrateres').text())
            end
            return {
                html = splash:html(),
                url = splash:url(),
            }
        end
        """

    def parse_item(self,response):
        review = ReviewItem()
        review['product_name']  = response.meta['product_name']
        get_reviews = Selector(response).xpath('//div[@id="listRate"]/div[@class="fs-dttrateitem"]')

        for get_review in get_reviews:
            if(self.count_crawl < self.limit):
                review['reviewer_name'] = get_review.xpath('div[@class="fs-dttrcre"]/ul[@class="fs-rtlul"]/li[1]/strong/text()').extract_first()        
                review['review_content'] = get_review.xpath('div[@class="fs-dttrtxt"]/text()').extract_first()
                review['review_content'] = review['review_content'].replace('\n','').strip()

                review['rating'] = len(get_review.xpath('div[@class="fs-dttrate"]/ul/li/span[@class="fs-dttr10"]').extract())
                review['date_crawl_product'] = self.timestamp
                review['product_provider'] = 2
                review['link_image_review'] = ""
                self.count_crawl += 1
                yield review
            else:
                print("Da crawl xong 40 lan")
                self.count_crawl = 0
                return
        



