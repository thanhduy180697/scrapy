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
from scrapy.shell import inspect_response

class CrawlerSpider(Spider):
    name = "crawler_specifications_dienmaycholon"
    
    allowed_domains = ["dienmaycholon.vn"]
    start_urls = [
        "https://dienmaycholon.vn/dien-thoai-di-dong"
    ]
    link_product = {}
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
            #yield SplashRequest(url="https://dienmaycholon.vn/dien-thoai-di-dong/oppo-a5s-32gb",callback=self.parse_item, args= {"wait" : 3})
            yield SplashRequest(url=url,callback=self.parse, args= {"wait" : 3},meta={
                            "splash": {"endpoint": "execute", "args": {"lua_source": self.script}}})
        
    def parse(self, response):
        
        products = Selector(response).xpath('//ul[@class="list_productcate"]/li')
        
        for product in products:
            product_name = product.xpath('div[@class="item_product"]/div[@class="pro_infomation"]/a/@title').extract_first()
            product_name = product_name.replace('Di \u0110\u1ed9ng ','').replace('B\u1ed9 S\u1ea3n Ph\u1ea9m ','')
            link = response.urljoin(product.xpath('div[@class="item_product"]/div[@class="pro_infomation"]/a/@href').extract_first()) 
            self.link_product.update({'{}'.format(link) : '{}'.format(product_name)})

        for key,value in self.link_product.items():
            yield SplashRequest(url=key,callback=self.parse_item,args= {"wait" : 3} , meta = {"product_name" : value})              

    def parse_item(self,response):
        product_name  = response.meta['product_name']

        item = SpecificationItem()
        item['display'] = None
        item['front_camera'] = None
        item['operating_system'] = None
        item['rear_camera'] = None
        item['battery'] = None
        item['storage'] = None
        item['ram'] = None
        item['cpu'] = None
        item['brand'] = None

        for i in range(10):
            item_information=response.xpath('//div[@class="special_list_property"]/ul/li[{}]/text()'.format(i+1)).extract_first()    
            item_sub=response.xpath('//div[@class="info_highlight"]/div[@class="tHead"]/div[{}]/text()'.format(i+1)).extract_first()
            value_sub=response.xpath('//div[@class="info_highlight"]/div[@class="tRow"]/div[{}]/text()'.format(i+1)).extract_first()
            if(item_information is not None):
                if(item_information.find('CPU') >= 0):
                    data = item_information[item_information.find(':')+1:]
                    cpu = data[:data.find('/') - 1]
                    item['cpu'] =  cpu.strip()

                if(item_information.find('Ram') >= 0):
                    data = item_information[item_information.find(':')+1:]
                    ram = data[:data.find('/') - 1]
                    item['ram'] =  ram.strip()
                    storage = data[data.find('/') + 1:]
                    item['storage'] =  storage.strip()

                if(item_information.find('Camera tr\u01b0\u1edbc') >= 0): 
                    data = item_information[item_information.find(':')+1:]
                    front_camera = data[:data.find('/') - 1]
                    item['front_camera'] =  front_camera.strip()
                    rear_camera = data[data.find('/') + 1:]
                    item['rear_camera'] =  rear_camera.strip()

                if(item_information.lower().find('pin') >= 0 ):
                     
                    data = item_information[item_information.find(':')+1:]
                    item['battery'] = data.strip()
                    if(item['battery'] is None):
                        if(item_sub is not None):
                            if(item_sub.lower().find('dung l\u01b0\u1ee3ng pin')>=0):
                                item['battery'] = value_sub
 
        str_operating = response.xpath('//div[@class="list_template list_template_active"]/div[@class="row_tem"][4]/div[@class="row_table"]/div[1]/text()').extract_first()
        if(str_operating is not None):
            if (str_operating.find('H\u1ec7 \u0111i\u1ec1u hành') >= 0):
                item['operating_system'] = response.xpath('//div[@class="list_template list_template_active"]/div[@class="row_tem"][4]/div[@class="row_table"]/div[2]/text()').extract_first()
        
        display=""
        for i in range(1,5):
            str = response.xpath('//div[@class="list_template list_template_active"]/div[@class="row_tem"][3]/div[@class="row_table"][{}]/div[1]/text()'.format(i)).extract_first()
            value =  response.xpath('//div[@class="list_template list_template_active"]/div[@class="row_tem"][3]/div[@class="row_table"][{}]/div[2]/text()'.format(i)).extract_first()
            if (str is not None and value is not None):
                if(str.find('Kích Th\u01b0\u1edbc Màn Hình') >=0 or str.find('Lo\u1ea1i màn hình') >=0 or str.find('Màu màn hình') >=0 or str.find('\u0110\u1ed9 phân gi\u1ea3i') >=0):
                    display += ', ' + value
        item['display'] = display
        item['brand'] = response.xpath('//a[@class="blue text_margin"]/@title').extract_first().capitalize()
        item['product_provider'] = 6
        item['date_crawl_product'] = self.timestamp
        item['product_name'] = product_name
        
        
        # if(item['front_camera'].find('Không') >= 0):
        #     item['front_camera'] = None
        # if(item['rear_camera'].find('Không') >= 0):
        #     item['rear_camera'] = None
        # if(item['storage'].find('Không') >= 0):
        #     item['storage'] = None
        # if(item['operating_system'].find('Không') >= 0):
        #     item['operating_system'] = None
        # if(item['battery'].find('Không') >= 0):
        #     item['battery'] = None
        # if(item['cpu'].find('Không') >= 0):
        #     item['cpu'] = None   
        # if(item['ram'].find('Không') >= 0):
        #     item['ram'] = None
    
        yield item

        itemRating = RatingItem()
        itemRating['average_rating'] = None
        itemRating['average_rating']= response.xpath('//div[@class="rating_detail"]/input[@checked="checked"]/@value').extract_first()

        itemRating['product_name']  = product_name
        itemRating['product_provider'] = 6
        yield itemRating



        


