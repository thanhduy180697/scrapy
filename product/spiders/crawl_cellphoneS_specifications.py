from scrapy import Spider
from scrapy.selector import Selector
from ..items import SpecificationItem
from scrapy.exceptions import NotConfigured
from scrapy_splash import SplashRequest
import urllib.request
from unidecode import unidecode
from urllib.parse import urljoin
import datetime
import time
from scrapy.shell import inspect_response
from collections import OrderedDict
class CrawlerSpider(Spider):
    name = "crawler_specifications_cellphoneS"
    
    allowed_domains = ["cellphones.com.vn"]
    start_urls = [
        "https://cellphones.com.vn/mobile.html"
    ]

    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    limit = 10
    count_crawl = 0
    index = 1
    page = 0
    count = 0

    script = """
        function main(splash)
            local url = splash.args.url
            assert(splash:go(url))
            assert(splash:wait(2))
            local element = splash:select('a#more-specific')
            if(element ~= nil) then
                assert(element:mouse_click())
                assert(splash:wait(0.5))
            end
            return {
                html = splash:html(),
                url = splash:url(),
            }
        end
        """

    def start_requests(self):
        # for url in self.start_urls:
        #     yield SplashRequest(url=url,callback=self.parse, args= {"wait" : 3})
        yield SplashRequest(url="https://cellphones.com.vn/reamle-c3i.html",callback=self.parse_item,args= {"wait" : 3},meta={
                            "splash": {"endpoint": "execute", "args": {"lua_source": self.script}} , "product_name" : "Realme C3i"})  
    def parse(self, response):
        
        products = Selector(response).xpath('//div[@class="products-container"]/ul[@class="cols cols-5"]/li')
        
        for product in products:
            price = product.xpath('div[@class="lt-product-group-info"]/div[@class="price-box"]/p[@class="special-price"]/span/text()').extract_first()
            if(price is None):
                price = product.xpath('div[@class="lt-product-group-info"]/div[@class="price-box"]/span[@class="regular-price"]/span/text()').extract_first()
            if (price != "\u0110\u0103ng k\xfd nh\u1eadn tin"):
                product_name = product.xpath('div[@class="lt-product-group-info"]/a/h3/text()').extract_first().replace('\t','').replace(' Chính h\xe3ng','').replace('\u0110i\u1ec7n Tho\u1ea1i ','').replace(' chính h\xe3ng','')
                link = product.xpath('div[@class="lt-product-group-info"]/a/@href').extract_first()
                url_item=response.urljoin(link)
                self.link_product.update({'{}'.format(url_item) : '{}'.format(product_name)})
                
                        
        if(self.index==1):
            self.page=int(response.xpath('//div[@class="pages"]/ul[@class="pagination"][1]/li[6]/a/text()').extract_first())
            self.index= self.index + 1
            for i in range(self.page-1):
                url_page = "https://cellphones.com.vn/mobile.html?p={}".format(i+2)
                yield SplashRequest(url=url_page,callback=self.parse, args= {"wait" : 1})
        self.count+=1
        count_product = 0
        product = OrderedDict(reversed(list(self.link_product.items())))
        if(self.count == self.page):
            for key,value in product.items():
                count_product += 1
                if(count_product == 20):
                    time.sleep(15)
                    count_product = 0
                yield SplashRequest(url=key,callback=self.parse_item,args= {"wait" : 3},meta={
                                    "splash": {"endpoint": "execute", "args": {"lua_source": self.script}} , "product_name" : value})  

    
    def parse_item(self,response):
        product_name  = response.meta['product_name']

        item = SpecificationItem()
        item['display'] = None
        item['front_camera'] = None
        item['operating_system'] = None
        item['rear_camera'] = None
        item['battery'] = 'Not update'
        item['storage'] = None
        item['ram'] = None
        item['cpu'] = None
        item['brand'] = None
        for i in range(27):
            item_information=response.xpath('//table[@id="tskt"]/tbody/tr[{}]/td[1]/text()'.format(i+1)).extract_first()
            item_value = response.xpath('//table[@id="tskt"]/tbody/tr[{}]/td[2]/text()'.format(i+1)).extract_first()
            collection_value = response.xpath('//table[@id="tskt"]/tbody/tr[{}]/td[2]/text()'.format(i+1)).getall() 
            if(item_information is None):
                item_information=response.xpath('//table[@id="tskt"]/tr[{}]/td[1]/text()'.format(i+1)).extract_first()
            if(item_value is None):
                item_value=response.xpath('//table[@id="tskt"]/tr[{}]/td[2]/text()'.format(i+1)).extract_first()
            if(collection_value is None):
                collection_value=response.xpath('//table[@id="tskt"]/tr[{}]/td[2]/text()'.format(i+1)).getall()

            if(item_information is not None):
                if(item_information == 'Lo\u1ea1i màn hình'): 
                    item['display'] =  item_value
                if(item_information == 'Kích th\u01b0\u1edbc màn hình' and item['display'] is not None): 
                    item['display'] += ' '+ item_value

                if(item_information == 'H\u1ec7 \u0111i\u1ec1u hành'): 
                    item['operating_system'] =  item_value
                if(item_information == 'Camera tr\u01b0\u1edbc'): 
                    str =  collection_value
                    item['front_camera'] = ''
                    if (str is not None):
                        for s in str:
                            item['front_camera'] = item['front_camera'] + ' ' + s
                    item['front_camera'] = item['front_camera'].strip()

                if(item_information == 'Camera sau'):
                    str =  collection_value
                    item['rear_camera'] = ''
                    if (str is not None):
                        for s in str:
                            item['rear_camera'] = item['rear_camera'] + ' ' + s
                    item['rear_camera'] = item['rear_camera'].strip()

                if(item_information == 'Pin'): 
                    item['battery'] =  item_value
                    if(item['battery'] is not None):
                        item['battery'] = item['battery'].replace('\t','').strip()
                if(item_information == 'B\u1ed9 nh\u1edb trong'): 
                    item['storage'] =  item_value
                    if(item_value.find('Không') >= 0):
                        item['storage'] =  None

                if(item_information.lower().find('ram') >=0 ):
                    item['ram'] = item_value
                    if(item_value.find(',') >= 0):
                        item['ram'] =  item_value[:item_value.find(',')+1]
                    
                if(item_information == 'CPU'): 
                    item['cpu'] =  item_value

                if(item_information == 'H\xe3ng s\u1ea3n xu\u1ea5t'): 
                    item['brand'] =  item_value
        
        if(item['display'] is None):
            item['display'] =  'Not update'
        if(item['brand'] is None):
            item['brand'] =  product_name[:product_name.find(' ')]
        item['product_provider'] = 3
        item['date_crawl_product'] = self.timestamp
        item['product_name'] = product_name.replace('\t','').replace(' Chính h\xe3ng','').replace('\u0110i\u1ec7n Tho\u1ea1i ','').replace(' chính h\xe3ng','')
        item['average_rating']= response.xpath('//p[@class="averageRatings"]/text()').extract_first()
        yield item



        


