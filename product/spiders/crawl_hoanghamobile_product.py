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
    name = "crawler_product_hoanghamobile"
    
    allowed_domains = ["hoanghamobile.com"]
    start_urls = [
        "https://hoanghamobile.com/dien-thoai-di-dong-c14.html?sort=0&type=4"
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
            yield SplashRequest(url=url,callback=self.parse, args= {"wait" : 3})


    def parse(self, response):

        products = Selector(response).xpath('//div[@class="product-list"]/div[@class="list-content"]/div[@class="row-item"]/div[@class="list-item"]')
        for product in products:
            name_product = product.xpath('div[@class="box-border"]/div[@class="product-name"]/h4/a/text()').extract_first()
            price = product.xpath('div[@class="product-price"]/text()').extract_first()
            if(name_product.find('C\u0169') < 0 and price != 'Liên h\u1ec7'):
                item = ProductItem()
                name_product = name_product.replace('-Chính h\xe3ng','').replace('- Chính h\xe3ng','').replace('Chính h\xe3ng','').replace('- Chính H\xe3ng','').replace('Chính H\xe3ng','').replace('- chính h\xe3ng','').strip()
                if(name_product.find('Masstel Play 20') >= 0):
                    name_product = 'Masstel Play 20'
                if(name_product.find('Masstel H860') >= 0):
                    name_product = 'Masstel H860'
                if(name_product.find('Masstel Fami 12') >= 0):
                    name_product = 'Masstel Fami 12'
                if(name_product.find('Itel P11') >= 0):
                    name_product = 'Itel P11'
                item['product_name'] = name_product.replace('- TBH- 222 Tr\u1ea7n Phú, Thanh Hóa','')
                
                item['product_price']= price
                if (item['product_price'] is not None):
                    item['product_price'] = item['product_price'].strip().replace(' \u20ab','')

                if (item['product_price'] == ''):
                    data = product.xpath('div[@class="product-price"]/text()').extract()
                    item['product_price'] = data[1].strip().replace(' \u20ab','')

                item['product_link'] = response.urljoin(product.xpath('div[@class="box-border"]/div[@class="product-name"]/h4/a/@href').extract_first())
                item['link_image'] = product.xpath('div[@class="box-border"]/div[@class="mosaic-block"]/div[@class="mosaic-backdrop"]/img/@src').extract_first()
          
                item['product_provider'] = 5
                item['date_crawl_product'] = self.timestamp
                yield item
        pages = response.xpath('//div[@class="pageing-container"]/div[@class="paging"]/a/text()').getall()
        length = len(pages)
        current_page = int(response.xpath('//div[@class="pageing-container"]/div[@class="paging"]/a[@class="current"]/text()').extract_first())
        if(pages[length-1] == 'Cu\u1ed1i »'):
            url_next_page = "https://hoanghamobile.com/dien-thoai-di-dong-c14.html?type=4&sort=0&p={}".format(current_page+1)
            yield SplashRequest(url=url_next_page,callback=self.parse, args= {"wait" : 3})
        else:
            if(int(pages[length-1]) != current_page):         
                url_next_page = "https://hoanghamobile.com/dien-thoai-di-dong-c14.html?type=4&sort=0&p={}".format(current_page+1)
                yield SplashRequest(url=url_next_page,callback=self.parse, args= {"wait" : 3})

       
#140