# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import mysql.connector as MySQLdb
from mysql.connector import Error
from product.items import ProductItem
from product.items import ReviewItem
from product.items import SpecificationItem

class ProductPipeline(object):
    def __init__(self):
        try:
            self.conn = MySQLdb.connect(host='localhost',database='compareprice',user='root',password='')
            self.cursor = self.conn.cursor()
            print("MySQL connection is connected")

        except MySQLdb.Error as error:
            print("Failed to connect MySQL: {}".format(error))

    def insert_price(self, item):
        if (item['product_price'] is not None):
            #Tim id cua product
            product_id = self.find_product_id(item['product_name'],item['product_provider'])
            if(product_id is None):
                return
            #kiem tra so luong price cua product neu >30 thi xoa cu tao moi
            query_check_count = """SELECT COUNT(*) FROM prices WHERE product_id = %s"""
            record = (product_id,)
            self.cursor.execute(query_check_count,record)
            count_result=self.cursor.fetchone()
            count=count_result[0]
            if(count>6):
                query_first_row = """DELETE FROM prices WHERE product_id = %s ORDER BY created_at ASC LIMIT 1"""
                self.cursor.execute(query_first_row,record)
                self.conn.commit()
                print("Deleted record have older day")
            #Them record price vao bang
            query_price= """INSERT INTO prices (product_price, product_id, created_at) VALUES(%s, %s, %s)"""   
            recordPrice = (item['product_price'],product_id,item['date_crawl_product'])
            self.cursor.execute(query_price,recordPrice)
            self.conn.commit()
            print("Record price created successfully ")
    def store_product(self, item):
        try:
            query_product= """INSERT INTO products (product_name, product_link, link_image, average_rating,provider_id, created_at) VALUES(%s, %s,%s ,%s,%s,%s)"""
            recordProduct = (item['product_name'], item['product_link'], item['link_image'],None,item['product_provider'], item['date_crawl_product'])
            self.cursor.execute(query_product,recordProduct)      
            self.conn.commit()
            print("Record product created successfully ")
        except MySQLdb.Error as e:
            print("Error {}: {}".format(e.args[0],  e.args[1].encode("utf-8")))
        self.insert_price(item)
        return item
    def store_review(self,item):
        try:
            #Tim id cua product
            product_id = self.find_product_id(item['product_name'],item['product_provider'])
            if(product_id is None):
                return
            #kiem tra so luong review cua product neu >30 thi xoa cu tao moi
            query_check_count = """SELECT COUNT(*) FROM reviews WHERE product_id = %s"""
            record = (product_id,)
            self.cursor.execute(query_check_count,record)
            count_result=self.cursor.fetchone()
            count=count_result[0]
            if(count>30):
                query_first_row = """DELETE FROM reviews WHERE product_id = %s ORDER BY created_at ASC LIMIT 1"""
                self.cursor.execute(query_first_row,record)
                self.conn.commit()
                print("Deleted record have older day")
            #Ghi record review vao bang
            query_review= """INSERT INTO reviews (reviewer_name, review_content, link_image_review, rating,product_id, created_at) VALUES(%s, %s, %s, %s,%s,%s)"""
            record_review = (item['reviewer_name'], item['review_content'], item['link_image_review'],item['rating'],product_id, item['date_crawl_product'])
            self.cursor.execute(query_review,record_review)      
            self.conn.commit()
            print("Record review created successfully ")
        except MySQLdb.Error as e:
            print("Error {}: {}".format(e.args[0], e.args[1].encode("utf-8")))
        return item

    def store_specification(self,item):
        try:
            #Tim id cua product
            product_id = self.find_product_id(item['product_name'],item['product_provider'])
            #Ghi record review vao bang
            if(product_id is not None):
                    query_specification= """UPDATE products SET average_rating = %s, display = %s, operating_system = %s, front_camera = %s, rear_camera = %s, battery = %s, ram = %s, cpu = %s, brand = %s, storage = %s, updated_at = %s WHERE id = %s"""
                    record_specification = (item['average_rating'], item['display'], item['operating_system'], item['front_camera'], item['rear_camera'], item['battery'], item['ram'], item['cpu'], item['brand'], item['storage'], item['date_crawl_product'],product_id)
                    self.cursor.execute(query_specification,record_specification)      
                    self.conn.commit()
                    print("Record specification updated successfully")
            else:
                return 
        except MySQLdb.Error as e:
            print("Error {}: {}".format(e.args[0], e.args[1].encode("utf-8")))
        return item
            
    def find_product_id(self,product_name,product_provider):
        query="""SELECT * FROM products WHERE product_name = %s AND provider_id = %s"""
        recordProduct = (product_name,product_provider)
        self.cursor.execute(query,recordProduct)      
        result=self.cursor.fetchone()
        if (result):
            product_id=result[0]
        else:
            product_id = None
        return product_id
        
    
    def updated_for_product(self,item,product_id):
        query_update_product= """UPDATE products SET link_image = %s, product_link = %s, updated_at = %s WHERE id=%s"""
        record = (item['link_image'],item['product_link'],item['date_crawl_product'],product_id)
        self.cursor.execute(query_update_product,record)      
        self.conn.commit()
        self.insert_price(item)
        print("Record product updated successfully ")

    def process_item(self, item, spider):
        if isinstance(item, ProductItem):
            product_id = self.find_product_id(item['product_name'],item['product_provider'])
            if(product_id is None):
                return self.store_product(item)
            else:
                return self.updated_for_product(item,product_id)
        if isinstance(item, SpecificationItem):
            return self.store_specification(item)
        elif isinstance(item, RatingItem):
            return self.updated_rating_for_product(item)
        else:
            return
        
