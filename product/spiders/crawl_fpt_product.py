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
# urllib.request.urlretrieve(item['link_image'], "image/{}.jpg".format(index))
# index = index + 1
class CrawlerSpider(Spider):
    name = "crawler_product_fpt"
    
    allowed_domains = ["fptshop.com.vn"]
    start_urls = [
        "https://fptshop.com.vn/dien-thoai?sort=gia-cao-den-thap&trang=1"
    ]
    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    limit = 10
    count_crawl = 0
    index = 1
    last_page = 0

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url=url,callback=self.parse, args= {"wait" : 3})


    def parse(self, response):
        
        questions = Selector(response).xpath('//div[@class="fs-carow clearfix fs-row4phone viewgrid"]/div[@class="fs-lpil"]')
        for question in questions:
            item = ProductItem()
            price = question.xpath('div[@class="fs-lpil-if"]/div[@class="fs-lpilname"]/div[@class="fs-lpil-price"]/p/text()').extract_first()
            product_name = question.xpath('a[@class="fs-lpil-img"]/@title').extract_first()
            if(price is not None and product_name.find('\u0110\u1ed3ng h\u1ed3') < 0 and product_name.find('V\xd2NG') < 0 and product_name.find('Vòng') < 0):
                item['product_name'] = product_name
                
                item['product_price'] = price
                item['product_price'] = item['product_price'].replace('\xa0\u20ab','').replace(' \u20ab','')
                
                item['product_link'] = response.urljoin(question.xpath('div[@class="fs-lpil-if"]/div[@class="fs-lpilname"]/h3[@class="fs-lpil-name"]/a/@href').extract_first())
                item['link_image'] = question.xpath('a[@class="fs-lpil-img"]/p/img/@data-original').extract_first()
                item['product_provider'] = 2
                item['date_crawl_product'] = self.timestamp

                yield item

        if(self.index==1):
            self.last_page=int(response.xpath('//div[@class="f-cmtpaging"]/a[2]/@data-page').extract_first())
            self.index= self.index + 1           
            for i in range(2,self.last_page+1):
                url_page = "https://fptshop.com.vn/dien-thoai?sort=gia-cao-den-thap&trang={}".format(i)
                yield SplashRequest(url=url_page,callback=self.parse, args= {"wait" : 1})
    
#Crawl duoc 165


