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
from collections import OrderedDict

class CrawlerSpider(Spider):
    name = "crawler_specifications_tgdd"
    
    allowed_domains = ["thegioididong.com"]
    start_urls = [
        "https://www.thegioididong.com/dtdd",
    ]
    ts = time.time()
    link_product = {}
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    limit = 10
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
            # yield SplashRequest(url="https://www.thegioididong.com/dtdd/xiaomi-redmi-note-9s",callback=self.parse_item, args= {"wait" :3}, meta = {"product_name" : "Xiaomi Redmi Note 9S"})
            yield SplashRequest(url=url,callback=self.parse, args= {"wait" :3},meta={
                                        "splash": {"endpoint": "execute", "args": {"lua_source": self.script}}})
    
    def parse(self, response):
        questions = Selector(response).xpath('//ul[@class="homeproduct  "]/li[@class="item"]')
        for question in questions:
            price = question.xpath('a/div[@class="price"]/strong/text()').extract_first()
            if(price is not None and question.xpath('a/label[@class="preorder"]').extract_first() is None):
                product_name = question.xpath('a/h3/text()').extract_first()
                url = question.xpath('a/@href').extract_first()
                url_item=response.urljoin(url)
                self.link_product.update({'{}'.format(url_item) : '{}'.format(product_name)})
                
        # list_product = OrderedDict(reversed(list(self.link_product.items())))
        list_product = self.link_product
        self.len_product = len(list_product)
        count_product = 0
        for key,value in list_product.items():
            count_product +=1
            # if(count_product >= 15):
            yield SplashRequest(url=key,callback=self.parse_item, args= {"wait" : 1} , meta = {"product_name" : value})      

    def parse_item(self,response):
        item = SpecificationItem()
        item['display'] = None
        item['front_camera'] = None
        item['operating_system'] = None
        item['rear_camera'] = None
        item['battery'] = None
        item['storage'] = None
        item['ram'] = None
        item['cpu'] = None
        item['average_rating'] = None
        for i in range(11):
            item_information=response.xpath('//ul[@class="parameter "]/li[{}]/span/text()'.format(i+1)).extract_first()
            item_information_temp=response.xpath('//ul[@class="parameter "]/li[{}]/span/a/text()'.format(i+1)).extract_first()

            item_value_main = response.xpath('//ul[@class="parameter "]/li[{}]/div/text()'.format(i+1)).extract_first()
            item_value_temp = response.xpath('//ul[@class="parameter "]/li[{}]/div/a/text()'.format(i+1)).extract_first()     
            
            if(item_information == 'Màn hình:'): 
                str = response.xpath('//ul[@class="parameter "]/li[{}]/div/a/text()'.format(i+1)).getall()
                item['display'] = ''
                if (str is not None):
                    for s in str:
                        item['display'] = item['display'] + ' ' + s
                item['display'] = item['display'] + item_value_main
                item['display'] = item['display'].replace(',','')

            if(item_information == 'H\u1ec7 \u0111i\u1ec1u hành:'): 
                item['operating_system'] =  item_value_main
                if(item['operating_system'] is None):
                    item['operating_system'] =  item_value_temp
            if(item_information == 'Camera tr\u01b0\u1edbc:'): 
                item['front_camera'] =  item_value_main
                if(item['front_camera'] is None):
                    item['front_camera'] =  item_value_temp                

            if(item_information == 'Camera sau:' or item_information == 'Camera:'):
                item['rear_camera'] =  item_value_main
                if(item['rear_camera'] is None):
                    item['rear_camera'] =  item_value_temp

            if(item_information == 'Dung l\u01b0\u1ee3ng pin:'): 
                item['battery'] =  item_value_main
                if(item['battery'] is None):
                    item['battery'] =  item_value_temp

            if(item_information == 'B\u1ed9 nh\u1edb trong:'): 
                item['storage'] =  item_value_main
                if(item['storage'] is None):
                    item['storage'] =  item_value_temp

            if(item_information == 'RAM:'): 
                item['ram'] =  item_value_main
                if(item['ram'] is None):
                    item['ram'] =  item_value_temp
            elif(item_information_temp == 'RAM:'):
                item['ram'] =  item_value_main
                if(item['ram'] is None):
                    item['ram'] =  item_value_temp
                    
            if(item_information == 'CPU:'):
                item['cpu'] =  item_value_main
                if(item['cpu'] is None):
                    item['cpu'] =  item_value_temp

        item['brand']=response.xpath('//ul[@class="breadcrumb"]/li[@class="brand"]/a/text()').extract_first()
        if(item['brand'] is not None):
            item['brand'] = item['brand'].strip().replace('\n','')
        item['date_crawl_product']=self.timestamp
        item['product_name']=response.meta['product_name']
        item['product_provider'] = 1
        item['average_rating']= response.xpath('//div[@class="toprt"]/div[@class="crt"]/div[@class="lcrt "]/@data-gpa').extract_first()
        yield item
        self.len_product -= 1
        print("Con lai so luong product can crawl la {}".format(self.len_product))


                     

