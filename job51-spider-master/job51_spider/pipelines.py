# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from twisted.enterprise import adbapi
import redis
from share import REDIS_DB,REDIS_PWD,REDIS_HOST,REDIS_PORT
from share import MYSQL_PORT,MYSQL_CHARSET,MYSQL_DATA_DB,MYSQL_PASSWD,MYSQL_USER,MYSQL_HOST
import pymysql
import hashlib
from scrapy.exceptions import DropItem
import scrapy
import os

 

# 异步写入mysql
class MysqlPipeline(object):
    # 初始化函数
    def __init__(self, db_pool,db_params):
        self.db_params = db_params
        self.db_pool = db_pool
        self.myredis = redis.Redis(host=REDIS_HOST, password=REDIS_PWD, port=REDIS_PORT, db=REDIS_DB)

    # 从settings配置文件中读取参数
    @classmethod
    def from_settings(cls,settings):
        # 用一个db_params接收连接数据库的参数
        db_params = dict(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWD,
            port=MYSQL_PORT,
            database=MYSQL_DATA_DB,
            charset=MYSQL_CHARSET,
            use_unicode=True,
            cursorclass = pymysql.cursors.DictCursor
        )
        # 创建连接池
        db_pool = adbapi.ConnectionPool('pymysql', **db_params)

        # 返回一个pipeline对象
        return cls(db_pool,db_params)

    # 处理item函数
    def process_item(self, item, spider):
        # 有数据来了，进行计数+1操作
        self.myredis.hincrby("@" + spider.name, 'insert_sql_count', 1)

        if not hasattr(item, 'table_name'):
            return item
        cols, values = zip(*item.items())
        mysql_table = item.table_name
        if self.myredis.sismember(mysql_table,item["hash_id"]):
            print("查询数据已存在")
        else:
            self.myredis.sadd(mysql_table,item["hash_id"].encode("utf8"))
            print("正在存入数据库")

            # 把要执行的sql放入连接池
            query = self.db_pool.runInteraction(self.insert_into,item.table_name, cols, values)
            # 如果sql执行发送错误,自动回调addErrBack()函数
            query.addErrback(self.handle_error, item, spider)

        # 返回Item
        return item

    # 处理sql函数
    def insert_into(self, cursor, table_name,cols, values):
        # 创建sql语句
        sql = "INSERT INTO `{}` ({}) VALUES ({})".format(
                        table_name,
                        ','.join(cols),
                        ','.join(['%s'] * len(values))
        )
        print(values)
        # 执行sql语句
        cursor.execute(sql,values)

    # 错误处理函数
    def handle_error(self, failure, item, spider):
        # #输出错误信息
        print('错误，需要重新连接数据库：',failure)
        # 重新连接数据库
        self.db_pool = adbapi.ConnectionPool('pymysql', **self.db_params)
        cols, values = zip(*item.items())
        # 把要执行的sql放入连接池
        query = self.db_pool.runInteraction(self.insert_into, item.table_name, cols, values)
        # 如果sql执行发送错误,自动回调addErrBack()函数
        query.addErrback(self.handle_error, item, spider)
