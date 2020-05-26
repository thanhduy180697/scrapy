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
    name = "crawler_specifications_viettelstore"
    
    allowed_domains = ["viettelstore.vn"]
    start_urls = [
        "https://viettelstore.vn/danh-muc/dien-thoai-010001.html"       
    ]
    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    limit = 10
    count_crawl = 0
    index = 1
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
        
        products = Selector(response).xpath('//div[@id="div_Danh_Sach_San_Pham"]/div')
        for product in products:
            price = product.xpath('a/div[@class="color-black txt-13"]/span/text()').extract_first()
            if(price != 'Liên h\u1ec7'):
                product_name = product.xpath('a/h2[@class="name"]/text()').extract_first()
                product_name = product_name.replace('- \u0110i\u1ec7n tho\u1ea1i ng\u01b0\u1eddi già','').replace('\u0110T ','').replace('\u0110TD\u0110 ','')
                link = product.xpath('a/@href').extract_first()
                link_item = response.urljoin(link)

                yield SplashRequest(url=link_item,callback=self.parse_item,args={"wait" : 2} , meta = {"product_name" : product_name})
                    

    def parse_item(self,response):
        product_name  = response.meta['product_name']
    
        item = SpecificationItem()
        if(product_name is None):
            return
        else:
            product_name = product_name.replace('- \u0110i\u1ec7n tho\u1ea1i ng\u01b0\u1eddi già','').replace('\u0110T ','').replace('\u0110TD\u0110 ','')
        
        brand =  product_name[:product_name.find(' ')]

        if(product_name.find('Homephone') > 0):
            item['brand'] = "Viettel"
        if(product_name.find('Masstel') > 0):
            item['brand'] = "Masstel"
        if(product_name.find('Coolpad') > 0):
            item['brand'] = "Coolpad"
        if(product_name.find('Wiko') > 0):
            item['brand'] = "Wiko"
        if(brand == "iPhone"):
            item['brand'] = "Apple"
        else:
            item['brand'] = brand

        item['operating_system'] = None
        item['display'] = None
        item['front_camera'] = None
        item['rear_camera'] = None
        item['battery'] = None
        item['storage'] = None
        item['ram'] = None
        item['cpu'] = None
        for i in range(15):
            item_information=response.xpath('//div[@class="digital "]/table/tbody/tr[{}]/td[1]/text()'.format(i+1)).extract_first()
            item_value = response.xpath('//div[@class="digital "]/table/tbody/tr[{}]/td[2]/text()'.format(i+1)).extract_first()      
            if(item_information == 'Màn hình:'): 
                item['display'] =  item_value

            if(item_information == 'H\u1ec7 \u0111i\u1ec1u hành:'): 
                item['operating_system'] =  item_value.replace('\t','')
                
            if(item_information == 'Camera tr\u01b0\u1edbc:'): 
                item['front_camera'] =  item_value
                if(item['front_camera'] == 'Không'):
                    item['front_camera'] =  None

            if(item_information == 'Camera sau:'):
                item['rear_camera'] =  item_value
                if(item['rear_camera'] == 'Không'):
                    item['rear_camera'] =  None

            if(item_information == 'Pin:'): 
                item['battery'] =  item_value.replace('\t','') 
            
            if(item_information == 'B\u1ed9 nh\u1edb trong:'): 
                item['storage'] =  item_value
                if(item['storage'] is not None):
                    item_value.replace('\t','') 

            if(item_information == 'RAM:'): 
                item['ram'] =  item_value.replace('\t','') 
            
            if(item_information == 'CPU:'): 
                item['cpu'] =  item_value.replace('\t','')

        item['product_provider'] = 4
        item['date_crawl_product'] = self.timestamp
        item['product_name'] = product_name
       
        rating_multi = 0
        rating_sum = 0
        temp = 5
        for row in range(1,5):            
            rat = response.xpath('//div[@class="detail-rating-chart"]/div[{}]/span[@class="rating-counter"]/text()'.format(row)).extract_first()
            if (rat is not None):
                rating_multi = rating_multi + int(rat) * temp
                rating_sum = rating_sum + int(rat)
                temp = temp - 1

        if(rating_multi == 0 or rating_sum == 0):
            item['average_rating'] = None
        else: 
            rating_item = round(rating_multi / rating_sum,2)
            item['average_rating'] = ''
            item['average_rating'] = item['average_rating'] + str(rating_item)

        yield item

     
        




        


