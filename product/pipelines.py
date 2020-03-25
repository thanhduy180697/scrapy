# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import mysql.connector as MySQLdb
from mysql.connector import Error
class ProductPipeline(object):
    def __init__(self):
        try:
            self.conn = MySQLdb.connect(host='localhost',database='compare_price',user='root',password='')
            self.cursor = self.conn.cursor()
            print("MySQL connection is connected")

        except MySQLdb.Error as error:
            print("Failed to connect MySQL: {}".format(error))

    def insert_price(self, item):
        if (item['product_price'] is not None):
            query="""SELECT * FROM products WHERE product_name = %s AND provider_id = %s"""
            recordProduct = (item['product_name'],1)
            self.cursor.execute(query,recordProduct)      
            result=self.cursor.fetchone()
            product_id=result[0]
            query_price= """INSERT INTO prices (product_price, product_id, created_at) VALUES(%s, %s, %s)"""   
            recordPrice = (item['product_price'],product_id,item['date_crawl_product'])
            self.cursor.execute(query_price,recordPrice)
            self.conn.commit()
            print("Record price created successfully ")

    def process_item(self, item, spider):
        try:
            query_product= """INSERT INTO products (product_name, product_link, link_image, average_rating,provider_id, specification_id, created_at) VALUES(%s, %s, %s, %s,%s,%s,%s)"""
            recordProduct = (item['product_name'], item['product_link'], item['link_image'],item['average_rating'],1,1, item['date_crawl_product'])
            self.cursor.execute(query_product,recordProduct)      
            self.conn.commit()
            print("Record product created successfully ")
        except MySQLdb.Error as e:
            print("Error {}: {}".format(e.args[0], e.args[1]))
        self.insert_price(item)
        return item
