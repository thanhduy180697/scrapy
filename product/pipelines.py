# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import mysql.connector as MySQLdb
from mysql.connector import Error
from datetime import datetime

class ProductPipeline(object):
    def __init__(self):
        try:
            self.conn = MySQLdb.connect(host='localhost',database='compare_price',user='root',password='')
            self.cursor = self.conn.cursor()
            print("MySQL connection is connected")
        except MySQLdb.Error as error:
            print("Failed to connect MySQL: {}".format(error))

    def process_item(self, item, spider):
        try:
            now = datetime.now()
            s2 = now.strftime("%d/%m/%Y, %H:%M:%S")
            query= """INSERT INTO products (product_name, product_link, link_image, average_rating,provider_id, specification_id, created_at) VALUES(%s, %s, %s, %s,%s,%s,%s) ON DUPLICATE KEY UPDATE created_at = %s"""
            recordTuple = (item['product_name'], item['product_link'], item['link_image'],item['average_rating'],1,1, item['date_crawl_product'],s2)
            self.cursor.execute(query,recordTuple)            
            self.conn.commit()
            print("Record created successfully ")     
        except MySQLdb.Error as e:
            print("Error {}: {}".format(e.args[0], e.args[1]))
        return item
