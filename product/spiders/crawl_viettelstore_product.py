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
    name = "crawler_product_viettelstore"
    
    allowed_domains = ["viettelstore.vn"]
    start_urls = [
        "https://viettelstore.vn/danh-muc/dien-thoai-010001.html"
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
            local element = splash:select('#div_Danh_Sach_San_Pham_loadMore_btn')
            local display = element:styles()['display']
            local find = string.find(display, "block")
            while (find ~= nil)
            do
                local element=splash:select('#div_Danh_Sach_San_Pham_loadMore_btn > a')
                assert(element:mouse_click())
                assert(splash:wait(2))
                local element = splash:select('#div_Danh_Sach_San_Pham_loadMore_btn')
                local display = element:styles()['display']
                find = string.find(display, "block")
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

        products = Selector(response).xpath('//div[@id="div_Danh_Sach_San_Pham"]/div')
        for product in products:
            price = product.xpath('a/div[@class="color-black txt-13"]/span/text()').extract_first()
            if(price != 'Liên h\u1ec7'):
                item = ProductItem()
                item['product_name'] = product.xpath('a/h2[@class="name"]/text()').extract_first()
                item['product_name'] = item['product_name'].replace('- \u0110i\u1ec7n tho\u1ea1i ng\u01b0\u1eddi già','').replace('\u0110T ','').replace('\u0110TD\u0110 ','')
                
                item['product_price']= price
                if (item['product_price'] is not None):
                    item['product_price'] = item['product_price'].replace(' \u20ab','')
                item['product_link'] = response.urljoin(product.xpath('a/@href').extract_first())
                item['link_image'] = product.xpath('a/div[@class="img"]/img/@src').extract_first()
                
                item['product_provider'] = 4
                item['date_crawl_product'] = self.timestamp
                yield item
           
# crawl 195
#159 25/5/2020
    

       



