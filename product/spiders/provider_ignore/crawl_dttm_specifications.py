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

class CrawlerSpider(Spider):
    name = "crawler_specifications_dttm"
    
    allowed_domains = ["didongthongminh.vn"]
    start_urls = [
        "https://didongthongminh.vn/dien-thoai-chinh-hang"
        # "https://didongthongminh.vn/dien-thoai-sieu-pin/xiaomi-mi-max-2-chinh-hang-dgw-4gb-128gb"
    ]
    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    limit = 10
    count_crawl = 0
    index = 1
    page = 0


    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url=url,callback=self.parse, args= {"wait" : 3})


    def parse(self, response):
        
        products = Selector(response).xpath('//ul[@class="products columns-5"]/li')
        
        for product in products:
            price_product = product.xpath('a/span[@class="price"]/span[@class="woocommerce-Price-amount amount"]/text()').extract_first()
            name_product = product.xpath('a/span[@class="dst_hproduct_title"]/span[@class="dst_primtitle"]/text()').extract_first()
            if(price_product is not None and len(price_product) > 2 and name_product.find('C\u0169') < 0):
                link = product.xpath('a/@href').extract_first()
                time.sleep(1.5)   
                yield SplashRequest(url=link,callback=self.parse_item,args={"wait" : 2})
                        
        display_button = response.xpath('//div[@class="lmp_load_more_button br_lmp_button_settings"]/@style').extract_first()

        if(display_button.find("block") > 0):
            url_next= response.xpath('//div[@class="lmp_load_more_button br_lmp_button_settings"]/a/@href').extract_first()
            yield SplashRequest(url=url_next,callback=self.parse, args= {"wait" : 2})

    def parse_item(self,response):
        # inspect_response(response,self)
        try:
            product_name  = response.xpath('//div[@class="dst_cproduct"]/div[@class="dst_single_title"]/h1/text()').extract_first()
        
            item = SpecificationItem()
            item['operating_system'] = None
            item['display'] = None
            item['front_camera'] = None
            item['rear_camera'] = None
            item['battery'] = None
            item['storage'] = None
            item['ram'] = None
            item['brand'] = None

            for i in range(13):
                item_information=response.xpath('//table[@class="shop_attributes"]/tbody/tr[{}]/th/text()'.format(i+1)).extract_first()
                item_value = response.xpath('//table[@class="shop_attributes"]/tbody/tr[{}]/td/p/a/text()'.format(i+1)).extract_first()      
                if(item_information == 'Màn hình'): 
                    item['display'] =  item_value

                if(item_information == 'H\u1ec7 \u0111i\u1ec1u hành'): 
                    item['operating_system'] =  item_value
                    
                if(item_information == 'Camera tr\u01b0\u1edbc'): 
                    item['front_camera'] =  item_value

                if(item_information == 'Camera sau'):
                    item['rear_camera'] =  item_value

                if(item_information == 'Pin'): 
                    item['battery'] =  item_value 
                
                if(item_information == 'B\u1ed9 nh\u1edb trong' or item_information == 'Th\u1ebb Nh\u1edb'): 
                    item['storage'] =  item_value

                if(item_information == 'RAM'): 
                    item['ram'] =  item_value 
                
                if(item_information == 'CPU'): 
                    item['cpu'] =  item_value
            brand = product_name[:product_name.find(' ')]
            if(brand.find('Google') > 0):
                item['brand'] = "HTC"
            if(brand.find('Kyocera') > 0 or brand.find('H\u1eafc Th\u1ea7n Long Siêu B\u1ec1n') > 0 or brand.find('CAT') > 0):
                item['brand'] = "Kyocera & CAT"
            if(brand.find('SKY') > 0 or brand.find('Pantech') > 0):
                item['brand'] = "Pantech - SKY"
            if(brand.find('Sharp') > 0 or brand.find('Docomo') > 0 or brand.find('Fujitsu') > 0 or brand.find('FUJITSU') > 0):
                item['brand'] = "Fujitsu & Sharp"
            if(brand.find('W') > 0 and len(brand) < 2):
                item['brand'] = "Wmobile"
            if(brand.find('iPhone') > 0):
                item['brand'] = "Apple"
            else:
                item['brand'] = brand
            
            item['product_provider'] = 4
            item['date_crawl_product'] = self.timestamp
            item['product_name'] = product_name
            yield item

        except:
            print("Đã bị lỗi")
        




        


