from scrapy import Spider
from scrapy.selector import Selector
from scrapy import Request
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
    name = "crawler_specifications_fpt"
    
    allowed_domains = ["fptshop.com.vn"]
    start_urls = [
        "https://fptshop.com.vn/dien-thoai?sort=gia-cao-den-thap&trang=1"
    ]
    ts = time.time()
    link_product = {}
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    limit = 10
    count_crawl = 0
    index = 1
    last_page = 0
    count = 0

    def start_requests(self):
        for url in self.start_urls:
           yield SplashRequest(url=url,callback=self.parse, args= {"wait" : 3})
            
       

    def parse(self, response):
        specifications = Selector(response).xpath('//div[@class="fs-carow clearfix fs-row4phone viewgrid"]/div[@class="fs-lpil"]')
        #inspect_response(response,self)
        for specification in specifications:          
            item = SpecificationItem()
            price = specification.xpath('div[@class="fs-lpil-if"]/div[@class="fs-lpilname"]/div[@class="fs-lpil-price"]/p/text()').extract_first()
            product_name = specification.xpath('a[@class="fs-lpil-img"]/@title').extract_first()
            item['display'] = None
            item['battery'] = None
            item['ram'] = None
            item['cpu'] = None
            item['operating_system'] =None
            if(price is not None and product_name.find('\u0110\u1ed3ng h\u1ed3') < 0 and product_name.find('V\xd2NG') < 0 and product_name.find('Vòng') < 0):
                item['display'] = specification.xpath('div[@class="fs-lpil-if"]/div[@class="fs-lpil-tsul"]/ul/li[1]/text()').extract_first()
                item['battery'] = specification.xpath('div[@class="fs-lpil-if"]/div[@class="fs-lpil-tsul"]/ul/li[3]/text()').extract_first()
                item['ram'] = specification.xpath('div[@class="fs-lpil-if"]/div[@class="fs-lpil-tsul"]/ul/li[4]/text()').extract_first()
                item['cpu'] = specification.xpath('div[@class="fs-lpil-if"]/div[@class="fs-lpil-tsul"]/ul/li[5]/text()').extract_first()
                item['operating_system'] = specification.xpath('div[@class="fs-lpil-if"]/div[@class="fs-lpil-tsul"]/ul/li[6]/text()').extract_first()
                
                if(item['operating_system'] == 'Không'):
                    item['operating_system'] = None
                if(item['ram'] == 'Không'):
                    item['ram'] = None
                if(item['cpu'] == 'Không'):
                    item['cpu'] = None

                if(item['display'] is not None):
                    item['display'].replace('\t','')
                if(item['battery'] is not None):
                    item['battery'].replace('\t','')
                if(item['ram'] is not None):
                    item['ram'].replace('\t','')
                if(item['cpu'] is not None):
                    item['cpu'].replace('\t','')
                if(item['operating_system'] is not None):
                    item['operating_system'].replace('\t','')

                item['product_provider'] = 2
                item['date_crawl_product'] = self.timestamp
                item['product_name'] = product_name
                item['front_camera'] = None
                item['rear_camera'] = None
                item['storage'] = None
                item['brand'] = None
                url= specification.xpath('div[@class="fs-lpil-if"]/div[@class="fs-lpilname"]/h3[@class="fs-lpil-name"]/a/@href').extract_first()
                url_item=response.urljoin(url)
                yield item
                self.link_product.update({'{}'.format(url_item) : item})

        if(self.index==1):
            self.last_page=int(response.xpath('//div[@class="f-cmtpaging"]/a[2]/@data-page').extract_first())
            self.index= self.index + 1           
            for i in range(2,self.last_page+1):
                url_page = "https://fptshop.com.vn/dien-thoai?sort=gia-cao-den-thap&trang={}".format(i)
                print("Day la trang {}".format(i))
                yield SplashRequest(url=url_page,callback=self.parse, args= {"wait" : 1})
        self.count = self.count + 1
        if(self.count == self.last_page):
            for key,value in self.link_product.items():
                if(value['product_name'].find('Nokia 2720 Flip 4G') < 0):
                    yield SplashRequest(url=key,callback=self.parse_item, meta = {"item" : value})
                else:
                    yield Request(url=key,callback=self.parse_item, meta = {"item" : value})
    
    def parse_item(self,response):
        item = SpecificationItem()

        item_temp = response.meta['item']

        item['product_provider'] = 2
        item['date_crawl_product'] = self.timestamp
        
        item['product_name'] =  item_temp['product_name']
        item['display'] = item_temp['display']
        item['battery'] = item_temp['battery']
        item['ram'] = item_temp['ram']
        item['cpu'] = item_temp['cpu']
        item['operating_system'] = item_temp['operating_system']

        item['front_camera'] = None
        item['rear_camera'] = None
        item['storage'] = None

        for i in range(12):
            item_information=response.xpath('//div[@class="fs-tsright"]/ul/li[{}]/label/text()'.format(i+1)).extract_first()
            item_value = response.xpath('//div[@class="fs-tsright"]/ul/li[{}]/span/text()'.format(i+1)).extract_first()      
            if(item_information == 'Camera tr\u01b0\u1edbc :'): 
                item['front_camera'] =  item_value 
            if(item_information == 'Camera sau :'): 
                item['rear_camera'] =  item_value 
            if(item_information == 'B\u1ed9 nh\u1edb trong :'): 
                item['storage'] =  item_value

        if(item['front_camera'] == 'Không'):
            item['front_camera'] = None
        if(item['rear_camera'] == 'Không'):
            item['rear_camera'] = None
        if(item['storage'] == 'Không'):
            item['storage'] = None    
        item['brand'] = response.xpath('//ul[@class="fs-breadcrumb"]/li[3]/a/text()').extract_first()
        yield item

        itemRating = RatingItem()
        itemRating['average_rating']= response.xpath('//div[@id="danh-gia-nhan-xet"]/div[@class="fs-dttrating"]/div[@class="fs-dtrt-row clearfix"]/div[@class="fs-dtrt-col fs-dtrt-c1"]/h5/text()').extract_first()
        if(itemRating['average_rating'] is not None):
            itemRating['average_rating'] = itemRating['average_rating'].replace('/5','').replace(',','.')
        itemRating['product_name']  = response.xpath('//ul[@class="fs-breadcrumb"]/li[@class="active"]/text()').extract_first()
        itemRating['product_provider'] = 2
        yield itemRating


