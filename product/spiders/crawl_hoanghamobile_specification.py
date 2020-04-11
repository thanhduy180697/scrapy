from scrapy import Spider
from scrapy.selector import Selector
from ..items import SpecificationItem
from ..items import RatingItem
from scrapy.exceptions import NotConfigured
from scrapy_splash import SplashRequest
import urllib.request
from unidecode import unidecode
from urllib.parse import urljoin
import datetime
import time
from collections import OrderedDict
from scrapy.shell import inspect_response

class CrawlerSpider(Spider):
    name = "crawler_specifications_hoanghamobile"
    
    allowed_domains = ["hoanghamobile.com"]
    start_urls = [
        "https://hoanghamobile.com/dien-thoai-di-dong-c14.html?sort=0&type=4"
    ]
    ts = time.time()
    link_product = {}
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    limit = 10
    count_crawl = 0
    index=1
    page = 0
    crawl = False

    script = """
        function main(splash)
            local url = splash.args.url
            assert(splash:go(url))
            assert(splash:wait(2))
            local element = splash:select('button#btnProp')
            if(element ~= nil) then
                assert(element:mouse_click())
                assert(splash:wait(1))
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

                name_product = name_product.replace('- TBH- 222 Tr\u1ea7n Phú, Thanh Hóa','').replace('-Chính h\xe3ng','').replace('- Chính h\xe3ng','').replace('Chính h\xe3ng','').replace('- Chính H\xe3ng','').replace('Chính H\xe3ng','').replace('- chính h\xe3ng','').strip()
                if(name_product.find('Masstel Play 20') >= 0):
                    name_product = 'Masstel Play 20'
                if(name_product.find('Masstel H860') >= 0):
                    name_product = 'Masstel H860'
                if(name_product.find('Masstel Fami 12') >= 0):
                    name_product = 'Masstel Fami 12'
                if(name_product.find('Itel P11') >= 0):
                    name_product = 'Itel P11'
                
                link = response.urljoin(product.xpath('div[@class="box-border"]/div[@class="product-name"]/h4/a/@href').extract_first())
                
                self.link_product.update({'{}'.format(link) : '{}'.format(name_product)})
                
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
            else:
                self.crawl = True
        
        count_product = 0
        reset = 0
        product = OrderedDict(reversed(list(self.link_product.items())))
        craped_product = 0
        if(self.crawl):
            for key,value in product.items():
                reset += 1
                count_product +=1
                if(reset == 15):
                    time.sleep(15)
                    reset = 0
                if(count_product >= 100):    
                    yield SplashRequest(url=key,callback=self.parse_item,args= {"wait" : 3} ,meta={
                                    "splash": {"endpoint": "execute", "args": {"lua_source": self.script}}, "product_name" : value}) 


    def parse_item(self,response):
        product_name  = response.meta['product_name']

        item = SpecificationItem()
        item['operating_system'] = None
        item['display'] = None
        item['front_camera'] = None
        item['rear_camera'] = None
        item['battery'] = None
        item['storage'] = None
        item['ram'] = None
        item['cpu'] = None
        item['brand'] = None
        display=''
        #inspect_response(response,self)
        for i in range(25):
            item_information=response.xpath('//div[@class="simple-prop"]/p[{}]/label/text()'.format(i+1)).extract_first()
            item_value = response.xpath('//div[@class="simple-prop"]/p[{}]/span/a/text()'.format(i+1)).extract_first()      
            item_information_sub = response.xpath('//table[@class="table tab-prop table-striped table-hover"]/tbody/tr[{}]/td[@class="text"]/label/text()'.format(i+1)).extract_first()
            value_sub= response.xpath('//table[@class="table tab-prop table-striped table-hover"]/tbody/tr[{}]/td[@class="data"]/a/text()'.format(i+1)).extract_first()
            if(item_information is not None):
                if(item_information.find('H\xe3ng s\u1ea3n xu\u1ea5t') >= 0): 
                    item['brand'] =  item_value

                if(item_information.find('H\u1ec7 \u0111i\u1ec1u hành:') >= 0): 
                    item['operating_system'] =  item_value
                    
                if(item_information == 'Camera tr\u01b0\u1edbc:'): 
                    item['front_camera'] =  item_value
                    if(item['front_camera'] == 'Không'):
                        item['front_camera'] =  None

                if(item_information == 'Máy \u1ea3nh chính:'):
                    item['rear_camera'] =  item_value

                if(item_information.find('Dung l\u01b0\u1ee3ng pin (mAh):') >=0): 
                    item['battery'] =  item_value
                
                if(item_information.find('B\u1ed9 nh\u1edb trong:') >=0): 
                    item['storage'] =  item_value

                if(item_information.find('RAM:') >= 0): 
                    item['ram'] =  item_value
                
                if(item_information.find('CPU') >= 0): 
                    item['cpu'] =  item_value

            if(item_information_sub is not None):

                if(item_information_sub.find('Máy \u1ea3nh ph\u1ee5') >= 0): 
                    item['front_camera'] =  value_sub

                if(item_information_sub.find('Ki\u1ec3u màn hình') >= 0): 
                    display +=  value_sub + ', '

                if(item_information_sub.find('Kích th\u01b0\u1edbc màn hình') >= 0): 
                    display +=  value_sub

        item['display'] = display
        item['product_provider'] = 5
        item['date_crawl_product'] = self.timestamp
        item['product_name'] = product_name
        yield item

    

       
#140